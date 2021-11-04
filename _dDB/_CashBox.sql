CREATE TABLE CashBox
(
  id                          INTEGER PRIMARY KEY   AUTOINCREMENT,
  amount                      BIGINT DEFAULT 0,
  createdAt                   TEXT DEFAULT CURRENT_TIMESTAMP
);