-- V1 : création de la table des adresses
-- code_postal en CHAR et non en INT : sinon "01000" deviendrait 1000
CREATE TABLE adresse (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero_rue  VARCHAR(10)  NOT NULL,
    nom_rue     VARCHAR(255) NOT NULL,
    ville       VARCHAR(100) NOT NULL,
    code_postal CHAR(5)      NOT NULL,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
