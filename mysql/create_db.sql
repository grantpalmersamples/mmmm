create database if not exists mmmm;
use mmmm;

drop table if exists contact;
drop table if exists slack;
drop table if exists email;
drop table if exists team;
drop table if exists team_member;

-- -----------------------------------------------------
-- Table `mmmm`.`contact`
-- -----------------------------------------------------
CREATE TABLE `mmmm`.`contact` (
  `c_id` INT NOT NULL,
  PRIMARY KEY (`c_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mmmm`.`slack`
-- -----------------------------------------------------
CREATE TABLE `mmmm`.`slack` (
  `c_id` INT NOT NULL,
  `username` VARCHAR(256) NOT NULL,
  PRIMARY KEY (`c_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  CONSTRAINT `c_id`
    FOREIGN KEY (`c_id`)
    REFERENCES `mmmm`.`contact` (`c_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mmmm`.`email`
-- -----------------------------------------------------
CREATE TABLE `mmmm`.`email` (
  `c_id` INT NOT NULL,
  `username` VARCHAR(256) NOT NULL,
  PRIMARY KEY (`c_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  CONSTRAINT `c_id`
    FOREIGN KEY (`c_id`)
    REFERENCES `mmmm`.`contact` (`c_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mmmm`.`group`
-- -----------------------------------------------------
CREATE TABLE `mmmm`.`group` (
  `g_id` INT NOT NULL AUTO_INCREMENT,
  `g_admin` INT NOT NULL,
  `g_name` VARCHAR(45) NOT NULL,
  INDEX `g_admin_idx` (`g_admin` ASC),
  PRIMARY KEY (`g_id`),
  CONSTRAINT `g_admin`
    FOREIGN KEY (`g_admin`)
    REFERENCES `mmmm`.`contact` (`c_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mmmm`.`group_member`
-- -----------------------------------------------------
CREATE TABLE `mmmm`.`group_member` (
  `g_id` INT NOT NULL,
  `c_id` INT NOT NULL,
  CONSTRAINT `g_id`
    FOREIGN KEY (`g_id`)
    REFERENCES `mmmm`.`group` (`g_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `c_id`
    FOREIGN KEY (`c_id`)
    REFERENCES `mmmm`.`contact` (`c_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
