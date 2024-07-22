CREATE TABLE `tecja7_pychat`.`registro` (
  `id` INT NOT NULL,
  `fecha_hora` DATETIME NULL DEFAULT current_timestamp(),
  `mensaje_enviado` VARCHAR(1000) NULL,
  `mensaje_recibido` VARCHAR(1000) NULL,
  `id_wa` VARCHAR(1000) NULL,
  `timestamp_wa` VARCHAR(45) NULL,
  `telefono_wa` VARCHAR(50) NULL,
  `telefono_from` VARCHAR(45) NULL,
  `profile_name` VARCHAR(45) NULL,
  `key` VARCHAR(100) NULL,
  `mensaje` TEXT(5000) NULL,
  `status` VARCHAR(45) NULL,
  `estado` VARCHAR(45) NULL,
  `bearer` VARCHAR(300) NULL,
  PRIMARY KEY (`id`))
COMMENT = 'registros de mensajes';