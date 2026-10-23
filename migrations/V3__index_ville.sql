-- V3 : index pour accélérer la recherche par ville du front utilisateurs
CREATE INDEX idx_adresse_ville ON adresse (ville);
