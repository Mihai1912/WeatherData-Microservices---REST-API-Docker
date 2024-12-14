CREATE TABLE IF NOT EXISTS Tari (
    id SERIAL PRIMARY KEY,
    nume_tara VARCHAR(100) NOT NULL UNIQUE,
    latitudine FLOAT NOT NULL,
    longitudine FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS Orase (
    id SERIAL PRIMARY KEY,
    id_tara INT NOT NULL REFERENCES Tari(id) ON DELETE CASCADE,
    nume_oras VARCHAR(100) NOT NULL,
    latitudine FLOAT NOT NULL,
    longitudine FLOAT NOT NULL,
    CONSTRAINT oras_unic UNIQUE (id_tara, nume_oras)
);

CREATE TABLE IF NOT EXISTS Temperaturi (
    id SERIAL PRIMARY KEY,
    valoare FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    id_oras INT NOT NULL REFERENCES Orase(id) ON DELETE CASCADE,
    CONSTRAINT temperatura_unic UNIQUE (id_oras, timestamp)
);
