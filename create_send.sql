CREATE TABLE mensajes_enviados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255),
    estado INT,
    idWA VARCHAR(255),
    imput VARCHAR(255),
    contacto VARCHAR(255),
    fecha_y_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
