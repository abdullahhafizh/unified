DROP TABLE IF EXISTS TransactionsNew;
CREATE TABLE TransactionsNew
(
      trxId           VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
      mid             VARCHAR(100),
      amount          BIGINT,
      baseAmount      BIGINT,
      adminFee        BIGINT,
      trxType         VARCHAR(100),
      cardNo          VARCHAR(100),
      paymentType     VARCHAR(150),
      paymentNotes    TEXT,
      productName     VARCHAR(100),
      productId       VARCHAR(100),
      traceNo         VARCHAR(100),
      targetCard      VARCHAR(100),
      bankId          VARCHAR(2),
      syncFlag        INT,
      createdAt       BIGINT
);

