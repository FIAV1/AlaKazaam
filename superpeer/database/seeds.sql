INSERT INTO `peers` (`session_id`, `ip`, `port`)
VALUES
('ABCD1234ABCD1234', '172.016.001.001|FC00:2001:db8a:a0b2:12f0:a13w:0001:0001', '50001'),
('EFGH1234EFGH1234', '172.016.001.002|FC00:2001:db8a:a0b2:12f0:a13w:0001:0002', '50002'),
('ILMN1234ILMN1234', '172.016.001.003|FC00:2001:db8a:a0b2:12f0:a13w:0001:0003', '50003'),
('OPQR1234OPQR1234', '172.016.001.004|FC00:2001:db8a:a0b2:12f0:a13w:0001:0004', '50004'),
('STUV1234STUV1234', '172.016.001.005|FC00:2001:db8a:a0b2:12f0:a13w:0001:0005', '50005');

INSERT INTO `files` (`file_md5`, `file_name`, `download_count`)
VALUES
('bf278a7d147358961d1f4051bddaa001', 'video001.mkv                                                                                        ', '00010'),
('bf278a7d147358961d1f4051bddaa002', 'video002.mkv                                                                                        ', '00020'),
('bf278a7d147358961d1f4051bddaa003', 'video003.mkv                                                                                        ', '00030'),
('bf278a7d147358961d1f4051bddaa004', 'video004.mkv                                                                                        ', '00040'),
('bf278a7d147358961d1f4051bddaa005', 'video005.mkv                                                                                        ', '00050'),
('bf278a7d147358961d1f4051bddaa006', 'video006.mkv                                                                                        ', '00060'),
('bf278a7d147358961d1f4051bddaa007', 'video007.mkv                                                                                        ', '00070'),
('bf278a7d147358961d1f4051bddaa008', 'video008.mkv                                                                                        ', '00080'),
('bf278a7d147358961d1f4051bddaa009', 'video009.mkv                                                                                        ', '00090'),
('bf278a7d147358961d1f4051bddaa010', 'video010.mkv                                                                                        ', '00100'),
('bf278a7d147358961d1f4051bddaa011', 'video011.mkv                                                                                        ', '00110'),
('bf278a7d147358961d1f4051bddaa012', 'video012.mkv                                                                                        ', '00120');

INSERT INTO `files_peers` (`file_md5`, `session_id`)
VALUES
('bf278a7d147358961d1f4051bddaa001', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa002', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa003', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa004', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa005', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa006', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa007', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa008', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa009', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa010', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa011', 'ABCD1234ABCD1234'),
('bf278a7d147358961d1f4051bddaa012', 'ABCD1234ABCD1234'),

('bf278a7d147358961d1f4051bddaa001', 'EFGH1234EFGH1234'),
('bf278a7d147358961d1f4051bddaa002', 'EFGH1234EFGH1234'),
('bf278a7d147358961d1f4051bddaa003', 'EFGH1234EFGH1234'),
('bf278a7d147358961d1f4051bddaa004', 'EFGH1234EFGH1234'),

('bf278a7d147358961d1f4051bddaa001', 'ILMN1234ILMN1234'),

('bf278a7d147358961d1f4051bddaa001', 'OPQR1234OPQR1234'),
('bf278a7d147358961d1f4051bddaa002', 'OPQR1234OPQR1234'),
('bf278a7d147358961d1f4051bddaa003', 'OPQR1234OPQR1234'),
('bf278a7d147358961d1f4051bddaa004', 'OPQR1234OPQR1234'),

('bf278a7d147358961d1f4051bddaa001', 'STUV1234STUV1234'),
('bf278a7d147358961d1f4051bddaa002', 'STUV1234STUV1234'),
('bf278a7d147358961d1f4051bddaa003', 'STUV1234STUV1234'),
('bf278a7d147358961d1f4051bddaa004', 'STUV1234STUV1234');

