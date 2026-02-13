-- 行政管理测试数据 —— 自动生成
-- 使用前请确保 meeting_rooms / room_bookings / office_supplies / supply_requests / expresses / visitors 表已创建
BEGIN;

DELETE FROM visitors;
DELETE FROM expresses;
DELETE FROM supply_requests;
DELETE FROM office_supplies;
DELETE FROM room_bookings;
DELETE FROM meeting_rooms;

-- 会议室
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (1, '朝阳厅', '3F', 20, '投影仪、白板、视频会议系统、麦克风', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (2, '望京厅', '3F', 16, '投影仪、白板、视频会议系统', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (3, '国贸厅', '5F', 12, '投影仪、白板、视频会议系统', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (4, '三里屯', '5F', 10, '投影仪、白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (5, '中关村', '7F', 8, '电视屏幕、白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (6, '西二旗', '7F', 8, '电视屏幕、白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (7, '上地厅', '9F', 6, '电视屏幕、白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (8, '亦庄厅', '9F', 6, '电视屏幕', 'maintenance', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (9, '洽谈室A', '3F', 4, '白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) VALUES (10, '洽谈室B', '5F', 4, '白板', 'available', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');

-- 会议室预订
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (1, 7, 7, '客户演示', '2026-02-04 15:00:00', '2026-02-04 15:30:00', 'completed', '2026-01-31 15:00:00', '2026-01-31 15:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (2, 3, 8, '技术评审', '2026-02-03 14:00:00', '2026-02-03 16:00:00', 'completed', '2026-01-31 14:00:00', '2026-01-31 14:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (3, 7, 5, '1v1 面谈', '2026-02-04 09:30:00', '2026-02-04 11:00:00', 'completed', '2026-02-02 09:30:00', '2026-02-02 09:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (4, 4, 15, '架构讨论', '2026-02-05 10:00:00', '2026-02-05 10:30:00', 'completed', '2026-01-31 10:00:00', '2026-01-31 10:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (5, 8, 17, '周例会', '2026-02-14 15:30:00', '2026-02-14 17:30:00', 'cancelled', '2026-02-09 15:30:00', '2026-02-09 15:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (6, 2, 16, '需求讨论', '2026-02-11 09:00:00', '2026-02-11 10:00:00', 'completed', '2026-02-07 09:00:00', '2026-02-07 09:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (7, 5, 1, '架构讨论', '2026-02-03 09:00:00', '2026-02-03 11:00:00', 'completed', '2026-01-31 09:00:00', '2026-01-31 09:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (8, 4, 14, '客户演示', '2026-02-15 09:30:00', '2026-02-15 11:00:00', 'active', '2026-02-10 09:30:00', '2026-02-10 09:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (9, 10, 20, '培训分享', '2026-02-04 11:30:00', '2026-02-04 13:30:00', 'cancelled', '2026-01-30 11:30:00', '2026-01-30 11:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (10, 6, 14, '头脑风暴', '2026-01-31 15:30:00', '2026-01-31 17:30:00', 'completed', '2026-01-27 15:30:00', '2026-01-27 15:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (11, 6, 2, '周例会', '2026-02-09 10:30:00', '2026-02-09 12:00:00', 'completed', '2026-02-04 10:30:00', '2026-02-04 10:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (12, 1, 10, '需求讨论', '2026-01-31 11:00:00', '2026-01-31 12:00:00', 'cancelled', '2026-01-30 11:00:00', '2026-01-30 11:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (13, 7, 16, '架构讨论', '2026-02-03 15:30:00', '2026-02-03 16:00:00', 'cancelled', '2026-01-29 15:30:00', '2026-01-29 15:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (14, 3, 16, '1v1 面谈', '2026-02-20 14:30:00', '2026-02-20 15:00:00', 'active', '2026-02-15 14:30:00', '2026-02-15 14:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (15, 10, 15, '项目复盘', '2026-02-07 15:00:00', '2026-02-07 15:30:00', 'completed', '2026-02-05 15:00:00', '2026-02-05 15:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (16, 4, 13, '架构讨论', '2026-02-18 16:00:00', '2026-02-18 18:00:00', 'cancelled', '2026-02-13 16:00:00', '2026-02-13 16:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (17, 7, 8, '产品评审', '2026-02-19 09:30:00', '2026-02-19 11:00:00', 'active', '2026-02-15 09:30:00', '2026-02-15 09:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (18, 6, 12, '头脑风暴', '2026-02-11 15:30:00', '2026-02-11 17:00:00', 'completed', '2026-02-06 15:30:00', '2026-02-06 15:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (19, 7, 6, '1v1 面谈', '2026-02-05 11:00:00', '2026-02-05 12:30:00', 'completed', '2026-02-02 11:00:00', '2026-02-02 11:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (20, 7, 17, '设计评审', '2026-02-20 16:30:00', '2026-02-20 17:30:00', 'active', '2026-02-17 16:30:00', '2026-02-17 16:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (21, 3, 1, '需求讨论', '2026-02-02 16:30:00', '2026-02-02 18:30:00', 'cancelled', '2026-01-30 16:30:00', '2026-01-30 16:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (22, 4, 11, '头脑风暴', '2026-02-03 13:00:00', '2026-02-03 14:00:00', 'completed', '2026-01-31 13:00:00', '2026-01-31 13:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (23, 3, 11, '产品评审', '2026-02-15 09:00:00', '2026-02-15 10:30:00', 'active', '2026-02-14 09:00:00', '2026-02-14 09:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (24, 4, 11, '全员大会', '2026-02-16 14:30:00', '2026-02-16 16:00:00', 'active', '2026-02-14 14:30:00', '2026-02-14 14:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (25, 7, 13, 'Sprint 规划', '2026-02-12 09:30:00', '2026-02-12 10:30:00', 'completed', '2026-02-10 09:30:00', '2026-02-10 09:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (26, 2, 13, '周例会', '2026-02-20 09:00:00', '2026-02-20 10:30:00', 'active', '2026-02-18 09:00:00', '2026-02-18 09:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (27, 9, 11, '培训分享', '2026-02-13 15:30:00', '2026-02-13 17:30:00', 'active', '2026-02-11 15:30:00', '2026-02-11 15:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (28, 2, 14, '1v1 面谈', '2026-02-06 11:30:00', '2026-02-06 13:00:00', 'completed', '2026-02-03 11:30:00', '2026-02-03 11:30:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (29, 2, 6, '客户演示', '2026-02-15 13:00:00', '2026-02-15 14:30:00', 'active', '2026-02-14 13:00:00', '2026-02-14 13:00:00');
INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) VALUES (30, 6, 7, '面试', '2026-02-18 10:30:00', '2026-02-18 11:00:00', 'cancelled', '2026-02-16 10:30:00', '2026-02-16 10:30:00');

-- 办公用品
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (1, 'A4 纸', '耗材', 200, '包', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (2, '签字笔（黑）', '文具', 500, '支', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (3, '签字笔（蓝）', '文具', 300, '支', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (4, '签字笔（红）', '文具', 100, '支', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (5, '笔记本', '文具', 150, '本', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (6, '便利贴', '文具', 200, '本', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (7, '文件夹', '文具', 100, '个', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (8, '订书机', '文具', 30, '个', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (9, '订书针', '耗材', 100, '盒', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (10, '白板笔', '耗材', 80, '支', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (11, '垃圾袋', '清洁', 500, '卷', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (12, '抽纸', '清洁', 300, '包', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (13, '洗手液', '清洁', 50, '瓶', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (14, '墨盒（黑）', '耗材', 20, '个', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');
INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) VALUES (15, 'USB-C 线', '耗材', 40, '条', '2026-02-13 15:29:26.994599', '2026-02-13 15:29:26.994599');

-- 申领单
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (1, 14, '[{"name": "笔记本", "quantity": 1}]', 'rejected', 9, '库存不足，请下月申领', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (2, 15, '[{"name": "垃圾袋", "quantity": 3}, {"name": "洗手液", "quantity": 1}]', 'pending', NULL, '', '2026-02-04 15:29:26', '2026-02-04 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (3, 18, '[{"name": "白板笔", "quantity": 4}]', 'rejected', 9, '库存不足，请下月申领', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (4, 16, '[{"name": "文件夹", "quantity": 5}]', 'pending', NULL, '', '2026-02-02 15:29:26', '2026-02-02 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (5, 11, '[{"name": "白板笔", "quantity": 4}]', 'rejected', 9, '库存不足，请下月申领', '2026-01-29 15:29:26', '2026-01-29 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (6, 18, '[{"name": "墨盒（黑）", "quantity": 2}]', 'pending', NULL, '', '2026-01-19 15:29:26', '2026-01-19 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (7, 10, '[{"name": "A4 纸", "quantity": 2}, {"name": "签字笔（黑）", "quantity": 5}]', 'pending', NULL, '', '2026-01-30 15:29:26', '2026-01-30 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (8, 12, '[{"name": "垃圾袋", "quantity": 3}, {"name": "洗手液", "quantity": 1}]', 'approved', 9, '已审批通过', '2026-01-24 15:29:26', '2026-01-24 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (9, 18, '[{"name": "便利贴", "quantity": 3}, {"name": "签字笔（蓝）", "quantity": 2}]', 'approved', 9, '已审批通过', '2026-01-23 15:29:26', '2026-01-23 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (10, 7, '[{"name": "白板笔", "quantity": 4}]', 'pending', NULL, '', '2026-02-04 15:29:26', '2026-02-04 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (11, 15, '[{"name": "A4 纸", "quantity": 2}, {"name": "签字笔（黑）", "quantity": 5}]', 'pending', NULL, '', '2026-02-09 15:29:26', '2026-02-09 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (12, 5, '[{"name": "笔记本", "quantity": 1}]', 'approved', 9, '已审批通过', '2026-01-31 15:29:26', '2026-01-31 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (13, 12, '[{"name": "便利贴", "quantity": 3}, {"name": "签字笔（蓝）", "quantity": 2}]', 'approved', 9, '已审批通过', '2026-02-06 15:29:26', '2026-02-06 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (14, 9, '[{"name": "订书机", "quantity": 1}, {"name": "订书针", "quantity": 2}]', 'pending', NULL, '', '2026-01-18 15:29:26', '2026-01-18 15:29:26');
INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) VALUES (15, 8, '[{"name": "A4 纸", "quantity": 2}, {"name": "签字笔（黑）", "quantity": 5}]', 'rejected', 9, '库存不足，请下月申领', '2026-02-05 15:29:26', '2026-02-05 15:29:26');

-- 快递
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (1, 'SF391361284653', 'receive', 12, '圆通', 'pending', NULL, '请尽快领取', '2026-02-07 15:29:26', '2026-02-07 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (2, 'ZT31836827991', 'receive', 11, 'EMS', 'pending', NULL, '请尽快领取', '2026-02-02 15:29:26', '2026-02-02 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (3, 'SF632302332407', 'receive', 12, '韵达', 'pending', NULL, '请尽快领取', '2026-02-11 15:29:26', '2026-02-11 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (4, 'ZT43412809195', 'receive', 6, 'EMS', 'pending', NULL, '请尽快领取', '2026-01-29 15:29:26', '2026-01-29 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (5, 'SF849764189684', 'receive', 15, '中通', 'sent', NULL, '', '2026-02-12 15:29:26', '2026-02-12 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (6, 'ZT26698570205', 'receive', 1, '韵达', 'picked_up', '2026-02-07 15:29:26', '', '2026-01-17 15:29:26', '2026-01-17 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (7, 'SF249968222422', 'receive', 13, '中通', 'sent', NULL, '', '2026-02-06 15:29:26', '2026-02-06 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (8, 'ZT44717213234', 'receive', 7, '京东', 'sent', NULL, '', '2026-01-19 15:29:26', '2026-01-19 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (9, 'SF807750505825', 'receive', 6, 'EMS', 'picked_up', '2026-02-03 15:29:26', '', '2026-01-18 15:29:26', '2026-01-18 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (10, 'ZT59016864371', 'receive', 16, '京东', 'picked_up', '2026-02-13 15:29:26', '', '2026-01-16 15:29:26', '2026-01-16 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (11, 'SF568972992905', 'send', 16, '韵达', 'sent', NULL, '', '2026-02-03 15:29:26', '2026-02-03 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (12, 'ZT94521035759', 'send', 13, '韵达', 'picked_up', '2026-02-13 15:29:26', '', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (13, 'SF553237223779', 'send', 6, '圆通', 'picked_up', '2026-02-08 15:29:26', '', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (14, 'ZT47576009676', 'send', 14, '京东', 'sent', NULL, '', '2026-01-22 15:29:26', '2026-01-22 15:29:26');
INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) VALUES (15, 'SF637976505391', 'send', 10, '顺丰', 'pending', NULL, '', '2026-02-09 15:29:26', '2026-02-09 15:29:26');

-- 访客
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (1, '王建国', '滴滴', '13868460304', 6, '2026-02-17', '16:00-17:00', '培训讲座', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (2, '李明华', '滴滴', '13892998790', 10, '2026-02-20', '09:00-10:00', '合同签署', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (3, '刘思远', '京东', '13861226266', 6, '2026-02-23', '10:00-11:00', '面试', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (4, '陈志强', '京东', '13813702997', 8, '2026-02-17', '09:00-10:00', '面试', 'cancelled', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (5, '张伟', '网易', '13855746641', 6, '2026-02-08', '10:00-11:00', '技术交流', 'cancelled', '2026-02-05 15:29:26', '2026-02-05 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (6, '赵丽', '百度', '13855824758', 5, '2026-02-10', '09:00-10:00', '培训讲座', 'checked_out', '2026-02-07 15:29:26', '2026-02-07 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (7, '杨洁', '美团', '13898868581', 3, '2026-02-16', '16:00-17:00', '商务拜访', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (8, '黄磊', '字节跳动', '13874765541', 1, '2026-02-17', '16:00-17:00', '合同签署', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (9, '周涛', '阿里巴巴', '13875335498', 1, '2026-02-11', '15:00-16:00', '审计检查', 'checked_out', '2026-02-08 15:29:26', '2026-02-08 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (10, '吴芳', '网易', '13890843190', 4, '2026-02-06', '14:00-15:00', '合同签署', 'checked_out', '2026-02-03 15:29:26', '2026-02-03 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (11, '林小林', '客户C', '13855974043', 18, '2026-02-14', '16:00-17:00', '技术交流', 'pending', '2026-02-11 15:29:26', '2026-02-11 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (12, '马超', '华为', '13868358502', 13, '2026-02-07', '09:00-10:00', '参观考察', 'checked_out', '2026-02-04 15:29:26', '2026-02-04 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (13, '孙学文', '客户C', '13818970993', 17, '2026-02-10', '15:00-16:00', '项目对接', 'cancelled', '2026-02-07 15:29:26', '2026-02-07 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (14, '朱凯', '网易', '13846108310', 2, '2026-02-19', '10:00-11:00', '技术交流', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');
INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) VALUES (15, '何雨婷', '百度', '13887266798', 11, '2026-02-18', '10:00-11:00', '商务拜访', 'pending', '2026-02-13 15:29:26', '2026-02-13 15:29:26');

COMMIT;