-- Drop existing tables in dependency order
DROP TABLE IF EXISTS CollectionItem;
DROP TABLE IF EXISTS Collection;
DROP TABLE IF EXISTS SoftwareFeature;
DROP TABLE IF EXISTS Evaluation;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS RegisteredUser;
DROP TABLE IF EXISTS Feature;
DROP TABLE IF EXISTS Software;
DROP TABLE IF EXISTS ProductType;
DROP TABLE IF EXISTS `User`;

-- 1. User
CREATE TABLE `User` (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(255) UNIQUE,
    RegisterDate DATE
);

-- 2. RegisteredUser
CREATE TABLE RegisteredUser (
    UserID INT PRIMARY KEY,
    Username VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (UserID) REFERENCES `User`(UserID)
);

-- 3. Admin
CREATE TABLE Admin (
    UserID INT PRIMARY KEY,
    AdminLevel INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES `User`(UserID)
);

-- 4. ProductType
CREATE TABLE ProductType (
    TypeID INT AUTO_INCREMENT PRIMARY KEY,
    TypeName VARCHAR(100) NOT NULL UNIQUE
);

-- 5. Software
CREATE TABLE Software (
    SoftwareID INT AUTO_INCREMENT PRIMARY KEY,
    Brand VARCHAR(255) NOT NULL,
    TypeID INT NOT NULL,
    ReleaseDate DATE,
    FOREIGN KEY (TypeID) REFERENCES ProductType(TypeID)
);

-- 6. Evaluation
CREATE TABLE Evaluation (
    EvaluationID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    SoftwareID INT NOT NULL,
    Friendliness INT NOT NULL,
    Price INT NOT NULL,
    Features INT NOT NULL,
    Accuracy INT NOT NULL,
    EvalDate DATE,

    FOREIGN KEY (UserID) REFERENCES `User`(UserID),
    FOREIGN KEY (SoftwareID) REFERENCES Software(SoftwareID),

    CHECK (Friendliness BETWEEN 1 AND 10),
    CHECK (Price BETWEEN 1 AND 10),
    CHECK (Features BETWEEN 1 AND 10),
    CHECK (Accuracy BETWEEN 1 AND 10)
);

-- 7. Feature
CREATE TABLE Feature (
    FeatureID INT AUTO_INCREMENT PRIMARY KEY,
    FeatureName VARCHAR(255) NOT NULL UNIQUE,
    Description TEXT
);

-- 8. SoftwareFeature
CREATE TABLE SoftwareFeature (
    SoftwareID INT NOT NULL,
    FeatureID INT NOT NULL,

    PRIMARY KEY (SoftwareID, FeatureID),

    FOREIGN KEY (SoftwareID) REFERENCES Software(SoftwareID),
    FOREIGN KEY (FeatureID) REFERENCES Feature(FeatureID)
);

-- 9. Collection
CREATE TABLE Collection (
    CollectionID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    CollectionName VARCHAR(255) NOT NULL,
    Description TEXT,
    CreateDate DATE,

    FOREIGN KEY (UserID) REFERENCES RegisteredUser(UserID)
);

-- 10. CollectionItem
CREATE TABLE CollectionItem (
    CollectionID INT NOT NULL,
    SoftwareID INT NOT NULL,

    PRIMARY KEY (CollectionID, SoftwareID),

    FOREIGN KEY (CollectionID) REFERENCES Collection(CollectionID),
    FOREIGN KEY (SoftwareID) REFERENCES Software(SoftwareID)
);
