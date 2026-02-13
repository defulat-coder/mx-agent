# admin-action-tools

员工操作工具 + 行政人员管理工具

## Requirements

### REQ-ADM-ACTION-1: adm_book_room

员工预订会议室。参数：room_id, title, start_time, end_time。
校验：30 分钟槽位对齐、时间冲突检测、最多提前 7 天。

### REQ-ADM-ACTION-2: adm_cancel_booking

员工取消预订。参数：booking_id。
校验：只能取消自己的预订、开始前 30 分钟可取消。

### REQ-ADM-ACTION-3: adm_request_supply

员工申领办公用品。参数：items（JSON 格式，[{name, quantity}]）。
创建 SupplyRequest，status=pending。

### REQ-ADM-ACTION-4: adm_book_visitor

员工预约访客。参数：visitor_name, company, phone, visit_date, visit_time, purpose。
创建 Visitor 记录，status=pending。

### REQ-ADM-ACTION-5: adm_apply_travel

员工申请差旅。不建表，返回审批链接。参数：destination, start_date, end_date, reason。

### REQ-ADM-ACTION-6: adm_admin_release_room

行政人员释放/维护会议室。参数：room_id, status（available/maintenance）。需 `admin_staff` 角色。

### REQ-ADM-ACTION-7: adm_admin_approve_supply

行政人员审批申领单。参数：request_id, action（approve/reject）, remark。
approved → 扣减库存。需 `admin_staff` 角色。

### REQ-ADM-ACTION-8: adm_admin_register_express

行政人员登记快递。参数：tracking_no, type, employee_id, courier, remark。需 `admin_staff` 角色。

## Scenarios

- 预订冲突 → 返回冲突信息而非异常
- 库存不足 → 审批通过时提示不足
- 差旅申请 → 返回格式：`{"approval_url": "https://oa.maxi.com/travel/apply?..."}`
- 行政管理工具的 ValueError 统一 catch 返回提示文字
