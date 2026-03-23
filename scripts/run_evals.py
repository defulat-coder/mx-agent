"""评测执行脚本 — 从 Langfuse Dataset 读取用例，双指标打分并上报"""
import argparse
import asyncio
import functools
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.core.tracing import setup_tracing
from app.evals.executor import HttpEvalRequester
from app.evals.judge import llm_judge
from app.evals.langfuse_eval import run_eval_experiment


def _parse_roles(raw: str) -> list[str]:
    roles = [r.strip() for r in raw.split(",") if r.strip()]
    return roles


def _build_auth_token(args: argparse.Namespace) -> str:
    if args.auth_token:
        return args.auth_token

    try:
        import jwt
    except ImportError as e:
        raise RuntimeError("缺少 pyjwt，无法自动生成评测登录态 token") from e

    payload = {
        "employee_id": args.employee_id,
        "roles": _parse_roles(args.roles),
        "department_id": args.department_id,
    }
    return jwt.encode(payload, settings.AUTH_SECRET, algorithm="HS256")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 Langfuse Dataset 执行评测并上报分数")
    parser.add_argument("--dataset-name", default="mx-agent-evals", help="Langfuse Dataset 名称")
    parser.add_argument("--run-name", default="", help="实验名称前缀，默认自动生成")
    parser.add_argument("--id-prefix", default="", help="按 case_id 前缀过滤，逗号分隔")
    parser.add_argument("--limit", type=int, default=0, help="最多执行条数，0=不限制")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Agent 接口地址")
    parser.add_argument("--endpoint", default="/teams/router-team/runs", help="接口路径")
    parser.add_argument(
        "--request-mode",
        choices=["auto", "json", "form"],
        default="auto",
        help="请求编码方式",
    )
    parser.add_argument("--message-field", default="message", help="请求体中的输入字段名")
    parser.add_argument("--auth-token", default="", help="Bearer Token（传入时优先使用）")
    parser.add_argument("--employee-id", type=int, default=9, help="自动生成 token 的 employee_id")
    parser.add_argument(
        "--roles",
        default="manager,admin,talent_dev,it_admin,admin_staff,finance,legal",
        help="自动生成 token 的 roles，逗号分隔",
    )
    parser.add_argument("--department-id", type=int, default=2, help="自动生成 token 的 department_id")
    parser.add_argument("--timeout", type=float, default=30.0, help="接口超时秒数")
    parser.add_argument("--concurrency", type=int, default=5, help="最大并发数")
    parser.add_argument("--judge-concurrency", type=int, default=2, help="LLM Judge 最大并发数")
    return parser


async def main_async(args: argparse.Namespace) -> None:
    """评测主逻辑（异步）。"""
    setup_tracing()
    auth_token = _build_auth_token(args)

    requester = HttpEvalRequester(
        base_url=args.base_url,
        endpoint=args.endpoint,
        timeout=args.timeout,
        auth_token=auth_token,
        message_field=args.message_field,
        request_mode=args.request_mode,
    )

    # 预绑定 LLM 配置，使 judge_fn 符合 (user_input, expected_behavior, response_text) 签名
    judge_fn = functools.partial(
        llm_judge,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    try:
        summary = await run_eval_experiment(
            dataset_name=args.dataset_name,
            run_name=args.run_name or None,
            requester=requester,
            judge_fn=judge_fn,
            id_prefix=args.id_prefix,
            limit=args.limit,
            concurrency=args.concurrency,
            judge_concurrency=args.judge_concurrency,
        )
    finally:
        await requester.close()

    print(f"run_name:      {summary.run_name}")
    print(f"总用例数:      {summary.total}")
    print(f"通过数:        {summary.passed}")
    print(f"工具匹配率:    {summary.tool_match_rate:.1%}")
    if summary.avg_response_quality is not None:
        print(f"平均回答质量:  {summary.avg_response_quality:.2f}")
    if summary.failed:
        top_n = min(5, len(summary.failed))
        print(f"失败用例 Top {top_n}:")
        for item in summary.failed[:top_n]:
            print(f"  - {item.case_id} | {item.fail_reason} | {item.response_preview[:60]}")


def main() -> None:
    """CLI 入口。"""
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
