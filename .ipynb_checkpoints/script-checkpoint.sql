PRAGMA foreign_keys = ON;

CREATE TABLE Customers (
    CustomerId INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerCode VARCHAR(50) UNIQUE NOT NULL,
    CustomerName TEXT NOT NULL,
    Email TEXT NULL,
    Phone TEXT NULL,
    BillingAddress1 TEXT NULL,
    BillingCity TEXT NULL,
    BillingCountry TEXT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    IsActive BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE Vendors (
    VendorId INTEGER PRIMARY KEY AUTOINCREMENT,
    VendorCode VARCHAR(50) UNIQUE NOT NULL,
    VendorName TEXT NOT NULL,
    Email TEXT NULL,
    Phone TEXT NULL,
    AddressLine1 TEXT NULL,
    City TEXT NULL,
    Country TEXT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    IsActive BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE Sites (
    SiteId INTEGER PRIMARY KEY AUTOINCREMENT,
    SiteCode VARCHAR(50) UNIQUE NOT NULL,
    SiteName TEXT NOT NULL,
    AddressLine1 TEXT NULL,
    City TEXT NULL,
    Country TEXT NULL,
    TimeZone TEXT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    IsActive BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE Locations (
    LocationId INTEGER PRIMARY KEY AUTOINCREMENT,
    SiteId INTEGER NOT NULL,
    LocationCode VARCHAR(50) NOT NULL,
    LocationName TEXT NOT NULL,
    ParentLocationId INTEGER NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    IsActive BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE (SiteId, LocationCode),
    FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
    FOREIGN KEY (ParentLocationId) REFERENCES Locations(LocationId)
);

CREATE TABLE Items (
    ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemCode TEXT UNIQUE NOT NULL,
    ItemName TEXT NOT NULL,
    Category TEXT NULL,
    UnitOfMeasure TEXT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    IsActive BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE Assets (
    AssetId INTEGER PRIMARY KEY AUTOINCREMENT,
    AssetTag VARCHAR(100) UNIQUE NOT NULL,
    AssetName TEXT NOT NULL,
    SiteId INTEGER NOT NULL,
    LocationId INTEGER NULL,
    SerialNumber TEXT NULL,
    Category TEXT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Active', -- Active, InRepair, Disposed
    Cost DECIMAL(18,2) NULL,
    PurchaseDate DATE NULL,
    VendorId INTEGER NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
    FOREIGN KEY (LocationId) REFERENCES Locations(LocationId),
    FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
);

CREATE TABLE Bills (
    BillId INTEGER PRIMARY KEY AUTOINCREMENT,
    VendorId INTEGER NOT NULL,
    BillNumber VARCHAR(100) NOT NULL,
    BillDate DATE NOT NULL,
    DueDate DATE NULL,
    TotalAmount DECIMAL(18,2) NOT NULL,
    Currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    Status VARCHAR(30) NOT NULL DEFAULT 'Open', -- Open, Paid, Void
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    UNIQUE (VendorId, BillNumber),
    FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
);

CREATE TABLE PurchaseOrders (
    POId INTEGER PRIMARY KEY AUTOINCREMENT,
    PONumber VARCHAR(100) NOT NULL,
    VendorId INTEGER NOT NULL,
    PODate DATE NOT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Open', -- Open, Approved, Closed, Cancelled
    SiteId INTEGER NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    UNIQUE (PONumber),
    FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId),
    FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
);

CREATE TABLE PurchaseOrderLines (
    POLineId INTEGER PRIMARY KEY AUTOINCREMENT,
    POId INTEGER NOT NULL,
    LineNumber INTEGER NOT NULL,
    ItemId INTEGER NULL,
    ItemCode TEXT NOT NULL,
    Description TEXT NULL,
    Quantity DECIMAL(18,4) NOT NULL,
    UnitPrice DECIMAL(18,4) NOT NULL,
    UNIQUE (POId, LineNumber),
    FOREIGN KEY (POId) REFERENCES PurchaseOrders(POId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);

CREATE TABLE SalesOrders (
    SOId INTEGER PRIMARY KEY AUTOINCREMENT,
    SONumber VARCHAR(100) NOT NULL,
    CustomerId INTEGER NOT NULL,
    SODate DATE NOT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Open', -- Open, Shipped, Closed, Cancelled
    SiteId INTEGER NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (datetime('now')),
    UpdatedAt DATETIME NULL,
    UNIQUE (SONumber),
    FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId),
    FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
);

CREATE TABLE SalesOrderLines (
    SOLineId INTEGER PRIMARY KEY AUTOINCREMENT,
    SOId INTEGER NOT NULL,
    LineNumber INTEGER NOT NULL,
    ItemId INTEGER NULL,
    ItemCode TEXT NOT NULL,
    Description TEXT NULL,
    Quantity DECIMAL(18,4) NOT NULL,
    UnitPrice DECIMAL(18,4) NOT NULL,
    UNIQUE (SOId, LineNumber),
    FOREIGN KEY (SOId) REFERENCES SalesOrders(SOId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);

CREATE TABLE AssetTransactions (
    AssetTxnId INTEGER PRIMARY KEY AUTOINCREMENT,
    AssetId INTEGER NOT NULL,
    FromLocationId INTEGER NULL,
    ToLocationId INTEGER NULL,
    TxnType VARCHAR(30) NOT NULL, -- Move, Adjust, Dispose, Create
    Quantity INTEGER NOT NULL DEFAULT 1,
    TxnDate DATETIME NOT NULL DEFAULT (datetime('now')),
    Note TEXT NULL,
    FOREIGN KEY (AssetId) REFERENCES Assets(AssetId),
    FOREIGN KEY (FromLocationId) REFERENCES Locations(LocationId),
    FOREIGN KEY (ToLocationId) REFERENCES Locations(LocationId)
);

CREATE INDEX IX_Customers_Code ON Customers(CustomerCode);
CREATE INDEX IX_Vendors_Code ON Vendors(VendorCode);
CREATE INDEX IX_Sites_Code ON Sites(SiteCode);
CREATE INDEX IX_Locations_Site_Code ON Locations(SiteId, LocationCode);
CREATE INDEX IX_Assets_Site_Status ON Assets(SiteId, Status);
CREATE INDEX IX_Assets_Location ON Assets(LocationId);
CREATE INDEX IX_Bills_BillDate ON Bills(BillDate);
CREATE INDEX IX_POs_Status_Date ON PurchaseOrders(Status, PODate);
CREATE INDEX IX_SOs_Customer_Date ON SalesOrders(CustomerId, SODate);
CREATE INDEX IX_POL_Item ON PurchaseOrderLines(ItemCode);
CREATE INDEX IX_SOL_Item ON SalesOrderLines(ItemCode);