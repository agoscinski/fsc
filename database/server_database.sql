-- MySQL Script generated by MySQL Workbench
-- 2016年10月26日 星期三 15时32分50秒
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema FSCDatabase
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema FSCDatabase
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `FSCDatabase` DEFAULT CHARACTER SET utf8 ;
USE `FSCDatabase` ;

-- -----------------------------------------------------
-- Table `FSCDatabase`.`AccountRole`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`AccountRole` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`AccountRole` (
  `RoleID` INT NOT NULL,
  `RoleName` VARCHAR(15) NULL,
  PRIMARY KEY (`RoleID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`Account`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`Account` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`Account` (
  `UserID` INT NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(30) NULL,
  `Password` VARCHAR(45) NULL,
  `SendInst` VARCHAR(45) NULL,
  `ClientID` VARCHAR(45) NULL,
  `RoleID` INT NULL,
  PRIMARY KEY (`UserID`),
  INDEX `fk_Account_AccountRole_idx` (`RoleID` ASC),
  CONSTRAINT `fk_Account_AccountRole`
    FOREIGN KEY (`RoleID`)
    REFERENCES `FSCDatabase`.`AccountRole` (`RoleID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`Stock`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`Stock` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`Stock` (
  `Ticker` VARCHAR(10) NOT NULL,
  `CompanyName` VARCHAR(45) NULL,
  `LotSize` INT NULL,
  `TickSize` DECIMAL(20,2) NULL,
  `TotalVolume` INT NULL,
  `CurrentPrice` DECIMAL(20,2) NULL,
  `CurrentVolume` INT NULL,
  PRIMARY KEY (`Ticker`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`Order`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`Order` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`Order` (
  `SendInst` VARCHAR(45) NOT NULL,
  `ClOrdID` VARCHAR(45) NOT NULL,
  `RecInst` VARCHAR(45) NULL,
  `ClientID` VARCHAR(45) NULL,
  `HandlInst` INT NULL,
  `Ticker` VARCHAR(6) NULL,
  `Side` INT NULL,
  `OrdType` INT NULL,
  `OrderQty` INT NULL,
  `CashOrderQty` DECIMAL(2) NULL,
  `Price` DECIMAL(2) NULL,
  `ReceivedTime` TIMESTAMP NULL,
  `LastStatus` INT NULL,
  `MsgSeqNum` INT NULL,
  PRIMARY KEY (`SendInst`, `ClOrdID`),
  INDEX `fk_Order_Account1_idx` (`ClientID` ASC, `SendInst` ASC),
  INDEX `fk_Order_Stock1_idx` (`Ticker` ASC),
  CONSTRAINT `fk_Order_Account1`
    FOREIGN KEY (`ClientID` , `SendInst`)
    REFERENCES `FSCDatabase`.`Account` (`ClientID` , `SendInst`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Order_Stock1`
    FOREIGN KEY (`Ticker`)
    REFERENCES `FSCDatabase`.`Stock` (`Ticker`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`OrderExecution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`OrderExecution` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`OrderExecution` (
  `ExecID` INT NOT NULL AUTO_INCREMENT,
  `BuySendInst` VARCHAR(45) NULL,
  `BuyClOrdID` VARCHAR(45) NULL,
  `SellSendInst` VARCHAR(45) NULL,
  `SellClOrdID` VARCHAR(45) NULL,
  `OrderExecQty` INT NULL,
  `OrderExecPrice` DECIMAL(2) NULL,
  `ExecTime` TIMESTAMP NULL,
  `OrderExecutioncol` VARCHAR(45) NULL,
  `MsgSeqNum` INT NULL,
  PRIMARY KEY (`ExecID`),
  INDEX `fk_OrderExecution_Order1_idx` (`BuySendInst` ASC, `BuyClOrdID` ASC, `SellSendInst` ASC, `SellClOrdID` ASC),
  CONSTRAINT `fk_OrderExecution_Order1`
    FOREIGN KEY (`BuySendInst` , `BuyClOrdID` , `SellSendInst` , `SellClOrdID`)
    REFERENCES `FSCDatabase`.`Order` (`SendInst` , `ClOrdID` , `SendInst` , `ClOrdID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`StockHistory`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`StockHistory` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`StockHistory` (
  `Ticker` VARCHAR(10) NOT NULL,
  `LastMatchPrice` DECIMAL(2) NULL,
  `LastMatchTime` DATETIME NULL,
  `LastOpenPrice` DECIMAL(2) NULL,
  `LastClosePrice` DECIMAL(2) NULL,
  `CurrentPrice` DECIMAL(2) NULL,
  `CurrentVolume` INT NULL,
  PRIMARY KEY (`Ticker`),
  INDEX `fk_StockHistory_Stock1_idx` (`Ticker` ASC),
  CONSTRAINT `fk_StockHistory_Stock1`
    FOREIGN KEY (`Ticker`)
    REFERENCES `FSCDatabase`.`Stock` (`Ticker`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`OrderCancel`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`OrderCancel` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`OrderCancel` (
  `SendInst` VARCHAR(45) NOT NULL,
  `ClOrdID` VARCHAR(45) NOT NULL,
  `RecInst` VARCHAR(45) NULL,
  `OrigClOrdID` VARCHAR(45) NULL,
  `Ticker` VARCHAR(45) NULL,
  `Side` INT NULL,
  `ReceivedTime` TIMESTAMP NULL,
  `LastStatus` INT NULL,
  `MsgSeqNum` INT NULL,
  PRIMARY KEY (`SendInst`, `ClOrdID`),
  CONSTRAINT `fk_OrderCancel_Order1`
    FOREIGN KEY (`SendInst` , `ClOrdID`)
    REFERENCES `FSCDatabase`.`Order` (`SendInst` , `ClOrdID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `FSCDatabase`.`OrderCancelExecution`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `FSCDatabase`.`OrderCancelExecution` ;

CREATE TABLE IF NOT EXISTS `FSCDatabase`.`OrderCancelExecution` (
  `SendInst` VARCHAR(45) NOT NULL,
  `ClOrdID` VARCHAR(45) NOT NULL,
  `CExecQty` INT NULL,
  `Exectime` TIMESTAMP NULL,
  `MsgSeqNum` INT NULL,
  INDEX `fk_OrderExecution_copy1_OrderCancel1_idx` (`SendInst` ASC, `ClOrdID` ASC),
  PRIMARY KEY (`SendInst`, `ClOrdID`),
  CONSTRAINT `fk_OrderExecution_copy1_OrderCancel1`
    FOREIGN KEY (`SendInst` , `ClOrdID`)
    REFERENCES `FSCDatabase`.`OrderCancel` (`SendInst` , `ClOrdID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

