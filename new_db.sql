DROP DATABASE IF EXISTS wpmb;
CREATE DATABASE wpmb;
USE wpmb;

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
	userID char(20) NOT NULL,
    password CHAR(80) NOT NULL,
    firstName CHAR(15) NOT NULL,
    lastName CHAR(15) NOT NULL,
    admin BOOLEAN NOT NULL,
    seller BOOLEAN NOT NULL,
    PRIMARY KEY (userID)
);

CREATE TABLE CreditCard (
    cardNumber CHAR(16) NOT NULL,
    expirationDate DATE NOT NULL,
    securityCode CHAR(3) NOT NULL,
    userID char(20) NOT NULL,
    PRIMARY KEY (cardNumber),
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

CREATE TABLE Address (
    addressID INT NOT NULL AUTO_INCREMENT,
    street CHAR(30) NOT NULL,
    city CHAR(30) NOT NULL,
    state CHAR(2) NOT NULL,
    zip CHAR(5) NOT NULL,
    userID char(20) NOT NULL,
    PRIMARY KEY (addressID),
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

CREATE TABLE Product (
    productID INT NOT NULL AUTO_INCREMENT,
    name CHAR(80) NOT NULL,
    startingPrice DECIMAL(5,2) NOT NULL,
    nltDate DATETIME NOT NULL,
    PRIMARY KEY (productID)
);

CREATE TABLE Ride (
    itemID INT NOT NULL AUTO_INCREMENT,
    productID INT NOT NULL,
    time DATETIME,
    departureFrom CHAR(30) NOT NULL,
    seatsAvailable INT NOT NULL,
    PRIMARY KEY (itemID),
    FOREIGN KEY (productID) REFERENCES Product(productID)
);

CREATE TABLE Book (
    itemID INT NOT NULL AUTO_INCREMENT,
    productID INT NOT NULL,
    author CHAR(60) NOT NULL,
    class CHAR(30) NOT NULL,
    PRIMARY KEY (itemID),
    FOREIGN KEY (productID) REFERENCES Product(productID)
);

CREATE TABLE UserSells (
    userID char(20) NOT NULL,
    productID INT NOT NULL,
    PRIMARY KEY (userID, productID),
    FOREIGN KEY (userID) REFERENCES Users(userID),
    FOREIGN KEY (productID) REFERENCES Product(productID)
);

CREATE TABLE UserBids (
    bidID INT NOT NULL AUTO_INCREMENT,
    userID char(20) NOT NULL,
    productID INT NOT NULL,
    bidAmount DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (bidID),
    FOREIGN KEY (userID) REFERENCES Users(userID),
    FOREIGN KEY (productID) REFERENCES Product(productID)
);


DELIMITER //

CREATE PROCEDURE ViewAllProducts()
BEGIN
    SELECT Product.productID, Product.name,
    Product.startingPrice, Product.nltDate,
    Ride.departureFrom,
    Ride.seatsAvailable, Ride.time,
    Book.author, Book.class
    FROM Product 
    LEFT JOIN Ride ON Product.productID = Ride.productID 
    LEFT JOIN Book ON Product.productID = Book.productID;
END //

CREATE PROCEDURE ViewAllRides()
BEGIN
    SELECT * FROM Ride JOIN Product ON Ride.productID = Product.productID;
END //

CREATE PROCEDURE ViewAllBooks()
BEGIN
    SELECT * FROM Book JOIN Product ON Book.productID = Product.productID;
END //

CREATE PROCEDURE BidOnProduct(
    userID char(20),
    productID INT,
    bidAmount DECIMAL(5,2)
)
BEGIN
    START TRANSACTION;
    INSERT INTO UserBids (userID, productID, bidAmount)
    VALUES (userID, productID, bidAmount);
    COMMIT;
END //

CREATE PROCEDURE ListBook(
    name CHAR(30),
    startingPrice DECIMAL(5,2),
    nltDate DATETIME,
    author CHAR(30),
    class CHAR(30),
    puserID char(20)
)
BEGIN
    START TRANSACTION;
    INSERT INTO Product (name, startingPrice, nltDate)
    VALUES (name, startingPrice, nltDate);
    SET @last_id = LAST_INSERT_ID();
    INSERT INTO Book (productID, author, class)
    VALUES (@last_id, author, class);
    INSERT INTO UserSells (userID, productID)
    VALUES (puserID, @last_id);
    UPDATE Users
    SET seller = 1
    WHERE userID = puserID;
    COMMIT;
END //

CREATE PROCEDURE ListRide(
    name CHAR(30),
    startingPrice DECIMAL(5,2),
    nltDate DATETIME,
    time DATETIME,
    departureFrom CHAR(30),
    seatsAvailable INT,
    puserID char(20)
)
BEGIN
    START TRANSACTION;
    INSERT INTO Product (name, startingPrice, nltDate)
    VALUES (name, startingPrice, nltDate);
    SET @last_id = LAST_INSERT_ID();
    INSERT INTO Ride (productID, time, departureFrom, seatsAvailable)
    VALUES (@last_id, time, departureFrom, seatsAvailable);
    INSERT INTO UserSells (userID, productID)
    VALUES (puserID, @last_id);
    UPDATE Users
    SET seller = 1
    WHERE userID = puserID;
    COMMIT;
END //

CREATE PROCEDURE ViewRide(
    productID INT
)
BEGIN
    SELECT * FROM Ride
    JOIN Product ON Ride.productID = Product.productID
    WHERE Ride.productID = productID;
END //

CREATE PROCEDURE ViewBook(
    productID INT
)
BEGIN
    SELECT * FROM Book
    JOIN Product ON Book.productID = Product.productID
    WHERE Book.productID = productID;
END //


CREATE PROCEDURE RemoveRide(
    pproductID INT
)
BEGIN
    START TRANSACTION;
    DELETE FROM UserSells
    WHERE productID = pproductID;

    DELETE FROM UserBids
    WHERE productID = pproductID;

    DELETE FROM Ride
    WHERE productID = pproductID;

    DELETE FROM Product
    WHERE productID = pproductID;
    COMMIT;
END //

CREATE PROCEDURE RemoveBook(
    pproductID INT
)
BEGIN
    START TRANSACTION;
    DELETE FROM UserSells
    WHERE productID = pproductID;

    DELETE FROM UserBids
    WHERE productID = pproductID;

    DELETE FROM Book
    WHERE productID = pproductID;

    DELETE FROM Product
    WHERE productID = pproductID;
    COMMIT;
END //

CREATE PROCEDURE AddUser(
    userID char(20),
    password CHAR(80),
    firstName CHAR(15),
    lastName CHAR(15),
    admin BOOLEAN,
    seller BOOLEAN,
    creditCard CHAR(16),
    expirationDate DATE,
    securityCode CHAR(3),
    street CHAR(30),
    city CHAR(30),
    state CHAR(2),
    zip CHAR(5)
)
BEGIN
    START TRANSACTION;
    INSERT INTO Users (userID, password, firstName, lastName, admin, seller)
    VALUES (userID, password, firstName, lastName, admin, seller);
    INSERT INTO CreditCard (cardNumber, expirationDate, securityCode, userID)
    VALUES (creditCard, expirationDate, securityCode, userID);
    INSERT INTO Address (street, city, state, zip, userID)
    VALUES (street, city, state, zip, userID);
    COMMIT;
END //

CREATE PROCEDURE UpdateCreditCard(
    new_cardNumber CHAR(16),
    new_expirationDate DATE,
    new_securityCode CHAR(3),
    puserID char(20)
)
BEGIN
    START TRANSACTION;
    UPDATE CreditCard
    SET expirationDate = new_expirationDate,
        securityCode = new_securityCode,
        cardNumber = new_cardNumber
    WHERE userID = puserID;
    COMMIT;
END //

CREATE PROCEDURE UpdateAddress(
    new_street CHAR(30),
    new_city CHAR(30),
    new_state CHAR(2),
    new_zip CHAR(5),
    puserID char(20)
)
BEGIN
    START TRANSACTION;
    UPDATE Address
    SET street = new_street,
        city = new_city,
        state = new_state,
        zip = new_zip
    WHERE userID = puserID;
    COMMIT;
END //

CREATE PROCEDURE RemoveUser(
    puserID char(20)
)
BEGIN
    SET SQL_SAFE_UPDATES = 0;

    START TRANSACTION;
    DELETE FROM CreditCard
    WHERE userID = puserID;
    DELETE FROM Address
    WHERE userID = puserID;
    DELETE FROM UserSells
    WHERE userID = puserID;

    DELETE FROM UserBids
    WHERE userID = puserID;

    DELETE FROM Ride
    WHERE productID IN (SELECT productID FROM UserSells WHERE userID = puserID);

    DELETE FROM Book
    WHERE productID IN (SELECT productID FROM UserSells WHERE userID = puserID);

    DELETE FROM Product
    WHERE productID IN (SELECT productID FROM UserSells WHERE userID = puserID);
    DELETE FROM Users
    WHERE userID = puserID;

    COMMIT;
END //

CREATE PROCEDURE GetBidsForProduct(
    productID INT
)
BEGIN
    SELECT * FROM UserBids
    WHERE UserBids.productID = productID;
END //

DELIMITER ;



SELECT * FROM Users;
SELECT * FROM CreditCard;
SELECT * FROM Address;
SELECT * FROM Book;


-- # Add a user
-- # admin
CALL AddUser('johndoe', 'JDJiJDEyJHVmM0FqWlFXMUU3SDhLb1VaN3BHdXVPV1UxdUZMLkVIL3NVSGgzbUQyZ2xGMG15UWM5YWcy', 'John', 'Doe', 1, 1, '1234567890123456', '2018-01-01', '123', '123 Main St', 'San Luis Obispo', 'CA', '93405');
-- # base users
CALL AddUser('sallydoe', 'JDJiJDEyJHVmM0FqWlFXMUU3SDhLb1VaN3BHdXVPV1UxdUZMLkVIL3NVSGgzbUQyZ2xGMG15UWM5YWcy', 'Sally', 'Doe', 0, 0, '1234567890122456', '2018-01-01', '123', '1213 Main St', 'San Luis Obispo', 'CA', '95405');
CALL AddUser('stevegill', 'JDJiJDEyJHVmM0FqWlFXMUU3SDhLb1VaN3BHdXVPV1UxdUZMLkVIL3NVSGgzbUQyZ2xGMG15UWM5YWcy', 'Steve', 'Gilland', 0, 0, '1234567890125456', '2018-01-01', '123', '124 Main St', 'San Luis Obispo', 'CA', '95405');
CALL AddUser('joebiden', 'JDJiJDEyJHVmM0FqWlFXMUU3SDhLb1VaN3BHdXVPV1UxdUZMLkVIL3NVSGgzbUQyZ2xGMG15UWM5YWcy', 'Joe', 'Biden', 0, 0, '1234567890125457', '2018-01-01', '123', '125 Main St', 'San Luis Obispo', 'CA', '95405');
CALL AddUser('ninaminer', 'JDJiJDEyJHVmM0FqWlFXMUU3SDhLb1VaN3BHdXVPV1UxdUZMLkVIL3NVSGgzbUQyZ2xGMG15UWM5YWcy', 'Nina', 'Miner', 0, 0, '1234567890125458', '2018-01-01', '123', '126 Main St', 'San Luis Obispo', 'CA', '95405');

SELECT * FROM Users;


DROP USER IF EXISTS 'admin'@'localhost';
DROP USER IF EXISTS 'buyer'@'localhost';
DROP USER IF EXISTS 'seller'@'localhost';
DROP USER IF EXISTS 'comp'@'localhost';
CREATE USER 'admin'@'localhost';
CREATE USER 'buyer'@'localhost';
CREATE USER 'seller'@'localhost';
CREATE USER 'comp'@'localhost';
 
GRANT EXECUTE ON PROCEDURE ViewAllProducts TO 'admin'@'localhost', 'buyer'@'localhost', 'seller'@'localhost', 'comp'@'localhost';
GRANT EXECUTE ON PROCEDURE ViewAllRides TO 'admin'@'localhost', 'buyer'@'localhost', 'seller'@'localhost', 'comp'@'localhost';
GRANT EXECUTE ON PROCEDURE ViewAllBooks TO 'admin'@'localhost', 'buyer'@'localhost', 'seller'@'localhost', 'comp'@'localhost';
GRANT EXECUTE ON PROCEDURE BidOnProduct TO 'buyer'@'localhost';
GRANT EXECUTE ON PROCEDURE ListRide TO 'seller'@'localhost';
GRANT EXECUTE ON PROCEDURE ListBook TO 'seller'@'localhost';
GRANT EXECUTE ON PROCEDURE RemoveRide TO 'seller'@'localhost';
GRANT EXECUTE ON PROCEDURE RemoveBook TO 'seller'@'localhost';
GRANT EXECUTE ON PROCEDURE AddUser TO 'admin'@'localhost';
GRANT EXECUTE ON PROCEDURE RemoveUser TO 'admin'@'localhost';
 
 
 
### TESTS ###

# Add a user

# Update user address
CALL UpdateAddress('123 Wall Street', 'New York City', 'NY', '10996', 'johndoe');

# Update user credit card
CALL UpdateCreditCard('1234567890123456', '2018-02-01', '666', 'johndoe');

# List a book
CALL ListBook('CSC 365', 10.00, '2018-01-01', 'John Doe', 'CSC 365', 'johndoe');
SELECT * FROM Book;

# List a ride
CALL ListRide('CSC 365', 10.00, '2018-01-01', '2018-01-01', 'San Luis Obispo', 4, 'johndoe');
SELECT * FROM Ride;

# Bid on a product
CALL BidOnProduct('johndoe', 1, 20.00);
SELECT * FROM UserBids;
CALL ViewAllProducts();
-- ### TESTS ###
 
