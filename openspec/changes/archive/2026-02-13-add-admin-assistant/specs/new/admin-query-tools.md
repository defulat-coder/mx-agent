# admin-query-tools

员工行政查询工具 + 行政人员查询/统计工具

## Requirements

### REQ-ADM-QUERY-1: adm_get_available_rooms

查询指定时间段可用的会议室列表。参数：start_time, end_time（可选，不传返回全部会议室）。
排除该时段有 active 预订的会议室。

### REQ-ADM-QUERY-2: adm_get_my_bookings

查询当前员工的会议室预订记录。参数：status（可选筛选）。

### REQ-ADM-QUERY-3: adm_get_my_express

查询当前员工的快递记录。参数：type（可选，receive/send）。

### REQ-ADM-QUERY-4: adm_get_my_visitors

查询当前员工的访客预约记录。参数：status（可选筛选）。

### REQ-ADM-QUERY-5: adm_admin_get_all_bookings

行政人员查询所有预订记录。参数：room_id, status, date（均可选）。需 `admin_staff` 角色。

### REQ-ADM-QUERY-6: adm_admin_get_supply_requests

行政人员查询办公用品申领单。参数：status（可选）。需 `admin_staff` 角色。

### REQ-ADM-QUERY-7: adm_admin_get_supply_stock

行政人员查询库存。参数：category（可选）。需 `admin_staff` 角色。

### REQ-ADM-QUERY-8: adm_admin_get_all_express

行政人员查询所有快递记录。参数：status, type（可选）。需 `admin_staff` 角色。

### REQ-ADM-QUERY-9: adm_admin_get_visitors

行政人员查询访客预约。参数：date, status（可选）。需 `admin_staff` 角色。

### REQ-ADM-QUERY-10: adm_admin_usage_stats

行政人员查看使用统计。返回会议室使用率、用品消耗 top5 等。需 `admin_staff` 角色。

## Scenarios

- 员工工具通过 `get_employee_id` 获取身份
- 行政管理工具通过 `get_admin_staff_id` 校验角色
- 未授权返回提示文字而非报错
- 返回格式统一为 JSON 字符串
