CREATE TABLE IF NOT EXISTS Tari (
    id SERIAL PRIMARY KEY,
    nume VARCHAR(100) NOT NULL UNIQUE,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS Orase (
    id SERIAL PRIMARY KEY,
    idTara INT NOT NULL REFERENCES Tari(id) ON DELETE CASCADE,
    nume VARCHAR(100) NOT NULL,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    CONSTRAINT oras_unic UNIQUE (idTara, nume)
);

CREATE TABLE IF NOT EXISTS Temperaturi (
    id SERIAL PRIMARY KEY,
    valoare FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    idOras INT NOT NULL REFERENCES Orase(id) ON DELETE CASCADE,
    CONSTRAINT temperatura_unic UNIQUE (idOras, timestamp)
);
