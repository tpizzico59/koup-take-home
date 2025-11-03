-- Seed data from data_sheet.txt

-- Clear existing data
TRUNCATE TABLE appointments, departments, providers, insurances, self_pay_rates RESTART IDENTITY CASCADE;

-- Insert providers
INSERT INTO providers (first_name, last_name, certification, specialty) VALUES
('Meredith', 'Grey', 'MD', 'Primary Care'),
('Gregory', 'House', 'MD', 'Orthopedics'),
('Cristina', 'Yang', 'MD', 'Surgery'),
('Chris', 'Perry', 'FNP', 'Primary Care'),
('Temperance', 'Brennan', 'PhD, MD', 'Orthopedics');

-- Insert departments
INSERT INTO departments (provider_id, name, phone, address, hours) VALUES
-- Meredith Grey
(1, 'Sloan Primary Care', '(710) 555-2070', '202 Maple St, Winston-Salem, NC 27101', 'M-F 9am-5pm'),

-- Gregory House
(2, 'PPTH Orthopedics', '(445) 555-6205', '101 Pine St, Greensboro, NC 27401', 'M-W 9am-5pm'),
(2, 'Jefferson Hospital', '(215) 555-6123', '202 Maple St, Claremont, NC 28610', 'Th-F 9am-5pm'),

-- Cristina Yang
(3, 'Seattle Grace Cardiac Surgery', '(710) 555-3082', '456 Elm St, Charlotte, NC 28202', 'M-F 9am-5pm'),

-- Chris Perry
(4, 'Sacred Heart Surgical Department', '(339) 555-7480', '123 Main St, Raleigh, NC 27601', 'M-W 9am-5pm'),

-- Temperance Brennan
(5, 'Jefferson Hospital', '(215) 555-6123', '202 Maple St, Claremont, NC 28610', 'Tu-Th 10am-4pm');

-- Insert accepted insurances
INSERT INTO insurances (name) VALUES
('Medicaid'),
('United Health Care'),
('Blue Cross Blue Shield of North Carolina'),
('Aetna'),
('Cigna');

-- Insert self-pay rates
INSERT INTO self_pay_rates (specialty, cost) VALUES
('Primary Care', 150),
('Orthopedics', 300),
('Surgery', 1000);