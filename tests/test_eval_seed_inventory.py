from pathlib import Path

import pytest

from app.evals.seed_inventory import SeedInventory, SeedInventoryLookupError, parse_insert_values


ROOT = Path("/Users/cy/PycharmProjects/mx-agent")


def test_parse_insert_values_supports_multiline_batch_insert():
    sql_text = """
    INSERT INTO meeting_rooms (
        id, name, floor, capacity, equipment, status
    ) VALUES
    (1, '朝阳厅', '3F', 20, '投影仪、白板、视频会议系统、麦克风', 'available'),
    (2, '望京厅', '3F', 16, '白板、视频会议系统', 'available');
    """

    rows = parse_insert_values(sql_text, "meeting_rooms")

    assert len(rows) == 2
    assert rows[0]["name"] == "朝阳厅"
    assert rows[0]["equipment"] == "投影仪、白板、视频会议系统、麦克风"
    assert "、" in rows[0]["equipment"]


def test_seed_inventory_loads_project_seed_files_and_helpers_work():
    inventory = SeedInventory.from_project_seed_files()

    assert inventory.find_employee(employee_id=1)["name"] == "张三"
    assert inventory.find_department(department_id=7)["name"] == "后端组"
    assert inventory.find_department(department_id=7)["manager_id"] == 1
    assert inventory.find_available_room()["status"] == "available"
    assert inventory.find_pending_reimbursement()["status"] == "pending"
    assert inventory.find_open_it_ticket()["status"] == "open"


def test_from_project_seed_files_fails_fast_on_empty_required_table(monkeypatch):
    def fake_read_sql_file(path):
        name = path.name
        if name == "seed.sql":
            return """
            INSERT INTO employees (id, name, employee_no, department_id, position, level, hire_date, status, email, phone)
            VALUES (1, '张三', 'MX0001', 7, '高级后端工程师', 'P7', '2021-03-15', '在职', 'zhangsan@maxi.com', '13800000001');

            INSERT INTO departments (id, name, parent_id, manager_id)
            VALUES (7, '后端组', 2, NULL);

            INSERT INTO reimbursements (id, reimbursement_no, employee_id, type, amount, status, reviewer_id, review_remark, reviewed_at, department_id, created_at, updated_at)
            VALUES (1, 'FIN-R-0001', 1, '交通', 100.0, 'pending', NULL, '', NULL, 7, '2026-01-16 15:55:04', '2026-01-16 15:55:04');

            INSERT INTO it_tickets (id, ticket_no, type, title, description, status, priority, submitter_id, handler_id, resolution, resolved_at, created_at, updated_at)
            VALUES (1, 'IT-T-0001', 'repair', '笔记本无法开机', '详细描述：笔记本无法开机，影响正常办公', 'open', 'high', 1, NULL, '', NULL, '2025-12-29 06:03:55', '2025-12-29 06:03:55');
            """
        return ""

    monkeypatch.setattr("app.evals.seed_inventory._read_sql_file", fake_read_sql_file)

    with pytest.raises(SeedInventoryLookupError, match="Seed inventory table is empty: meeting_rooms"):
        SeedInventory.from_project_seed_files()
