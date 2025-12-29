CREATE DATABASE IF NOT EXISTS carebase;
USE carebase;

CREATE TABLE Abteilung (
    Name VARCHAR(100) PRIMARY KEY,
    Gebäude VARCHAR(100),
    Stockwerk VARCHAR(100)
);

CREATE TABLE Person (
    SVNr VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Adresse VARCHAR(255)
);

CREATE TABLE Patient (
    SVNr VARCHAR(10) PRIMARY KEY,
    Versicherungsträger VARCHAR(100),
    NACA_Score INT,
    FOREIGN KEY (SVNr) REFERENCES Person(SVNr) ON DELETE CASCADE,
    CHECK (NACA_Score BETWEEN 0 AND 7)
);

CREATE TABLE Arzt (
    SVNr VARCHAR(10) PRIMARY KEY,
    Fachrichtung VARCHAR(100),
    Position VARCHAR(100),
    Abteilungsname VARCHAR(100) NOT NULL,
    Vorgesetzter_SVNr VARCHAR(10),
    FOREIGN KEY (SVNr) REFERENCES Person(SVNr) ON DELETE CASCADE,
    FOREIGN KEY (Abteilungsname) REFERENCES Abteilung(Name) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Vorgesetzter_SVNr) REFERENCES Arzt(SVNr) ON DELETE SET NULL
);

CREATE TABLE Sachbearbeiter (
    SVNr VARCHAR(10) PRIMARY KEY,
    Rolle VARCHAR(100),
    Anstellungsverhältnis VARCHAR(100),
    FOREIGN KEY (SVNr) REFERENCES Person(SVNr) ON DELETE CASCADE
);

CREATE TABLE Termin (
    TerminID INT NOT NULL,
    Datum DATE NOT NULL,
    Uhrzeit TIME NOT NULL,
    Grund VARCHAR(255),
    SVNr_Patient VARCHAR(10) NOT NULL,
    SVNr_Arzt VARCHAR(10) NOT NULL,
    SVNr_Sachbearbeiter VARCHAR(10),
    
    PRIMARY KEY (SVNr_Patient, TerminID),
    FOREIGN KEY (SVNr_Patient) REFERENCES Patient(SVNr) ON DELETE CASCADE,
    FOREIGN KEY (SVNr_Arzt) REFERENCES Arzt(SVNr) ON DELETE RESTRICT,
    FOREIGN KEY (SVNr_Sachbearbeiter) REFERENCES Sachbearbeiter(SVNr) ON DELETE SET NULL,
    
    UNIQUE(SVNr_Arzt, Datum, Uhrzeit),
    UNIQUE(SVNr_Patient, Datum, Uhrzeit)
);

CREATE TABLE Behandlung (
    BehandlungsID INT PRIMARY KEY,
    Beschreibung TEXT,
    Kosten DECIMAL(10, 2),
    SVNr_Patient VARCHAR(10) NOT NULL,
    TerminID INT NOT NULL,
    FOREIGN KEY (SVNr_Patient, TerminID) REFERENCES Termin(SVNr_Patient, TerminID) ON DELETE CASCADE
    
);

CREATE TABLE Medikament (
    PZN INT PRIMARY KEY,
    Name VARCHAR(100),
    Wirkstoff VARCHAR(100)
);

CREATE TABLE Verabreichung (
    BehandlungsID INT NOT NULL,
    PZN INT NOT NULL,
    PRIMARY KEY (BehandlungsID, PZN),
    FOREIGN KEY (PZN) REFERENCES Medikament(PZN) ON DELETE RESTRICT,
    FOREIGN KEY (BehandlungsID) REFERENCES Behandlung(BehandlungsID) ON DELETE CASCADE
);