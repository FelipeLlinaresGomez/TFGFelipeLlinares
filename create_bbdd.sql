CREATE DATABASE  IF NOT EXISTS `TFG_FELIPE_LLINARES` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `TFG_FELIPE_LLINARES`;
-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: TFG_FELIPE_LLINARES
-- ------------------------------------------------------
-- Server version	8.0.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actuacion`
--

DROP TABLE IF EXISTS `actuacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actuacion` (
  `idActuacion` int NOT NULL AUTO_INCREMENT,
  `Plantilla_actuacion` int NOT NULL,
  `Plantillas` varchar(300) DEFAULT NULL,
  `Dia` varchar(300) DEFAULT NULL,
  `Origen` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`idActuacion`),
  KEY `plantilla_actuacion_idx` (`Plantilla_actuacion`),
  CONSTRAINT `plantilla_actuacion` FOREIGN KEY (`Plantilla_actuacion`) REFERENCES `plantilla_actuacion` (`idPlantillaActuacion`)
) ENGINE=InnoDB AUTO_INCREMENT=163184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dia_semana`
--

DROP TABLE IF EXISTS `dia_semana`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dia_semana` (
  `dia_semana` varchar(30) NOT NULL,
  PRIMARY KEY (`dia_semana`),
  UNIQUE KEY `dia_semana_UNIQUE` (`dia_semana`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dia_semana`
--

LOCK TABLES `dia_semana` WRITE;
/*!40000 ALTER TABLE `dia_semana` DISABLE KEYS */;
INSERT INTO `dia_semana` VALUES ('Domingo'),('Jueves'),('Lunes'),('Martes'),('Miercoles'),('No informado'),('Sabado'),('Viernes');
/*!40000 ALTER TABLE `dia_semana` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fecha`
--

DROP TABLE IF EXISTS `fecha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fecha` (
  `idFecha` int NOT NULL AUTO_INCREMENT,
  `Dia_semana` varchar(30) DEFAULT NULL,
  `Dia` varchar(30) DEFAULT NULL,
  `Mes` varchar(30) DEFAULT NULL,
  `Año` varchar(30) DEFAULT NULL,
  `Festividad_fecha_general` varchar(100) DEFAULT NULL,
  `Festividad_fecha_concreta` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`idFecha`),
  KEY `Dia_semana_fecha_idx` (`Dia_semana`),
  CONSTRAINT `Dia_semana_fecha` FOREIGN KEY (`Dia_semana`) REFERENCES `dia_semana` (`dia_semana`)
) ENGINE=InnoDB AUTO_INCREMENT=169436 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hecho`
--

DROP TABLE IF EXISTS `hecho`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hecho` (
  `Identificador_denuncia` varchar(100) NOT NULL,
  `Actuacion` int DEFAULT NULL,
  `Fecha` int DEFAULT NULL,
  `Lugar` int DEFAULT NULL,
  `Grupo_tipos` varchar(300) DEFAULT NULL,
  `Tipos` varchar(300) DEFAULT NULL,
  `Calificacion` varchar(300) DEFAULT NULL,
  `Grado_ejecucion` varchar(300) DEFAULT NULL,
  `Modus_operandi` varchar(300) DEFAULT NULL,
  `Relacionado_Tipos` varchar(300) DEFAULT NULL,
  `Tramo_horario` varchar(30) DEFAULT NULL,
  `Lugar_general` varchar(100) DEFAULT NULL,
  `Lugar_grupo_especifico` varchar(100) DEFAULT NULL,
  `Lugar_especificos` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Identificador_denuncia`),
  UNIQUE KEY `Identificador_UNIQUE` (`Identificador_denuncia`),
  KEY `Fecha_hecho_idx` (`Fecha`),
  KEY `Lugar_hecho_idx` (`Lugar`),
  KEY `Actuacion_hecho_idx` (`Actuacion`),
  KEY `Tramo_horario_hecho_idx` (`Tramo_horario`),
  CONSTRAINT `Actuacion_hecho` FOREIGN KEY (`Actuacion`) REFERENCES `actuacion` (`idActuacion`),
  CONSTRAINT `Fecha_hecho` FOREIGN KEY (`Fecha`) REFERENCES `fecha` (`idFecha`),
  CONSTRAINT `Lugar_hecho` FOREIGN KEY (`Lugar`) REFERENCES `lugar` (`idLugar`),
  CONSTRAINT `Tramo_horario_hecho` FOREIGN KEY (`Tramo_horario`) REFERENCES `tramo_horario` (`tramo_horario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lugar`
--

DROP TABLE IF EXISTS `lugar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lugar` (
  `idLugar` int NOT NULL AUTO_INCREMENT,
  `Continente` varchar(300) DEFAULT NULL,
  `Pais` varchar(300) DEFAULT NULL,
  `Jefatura` varchar(300) DEFAULT NULL,
  `Provincia` varchar(300) DEFAULT NULL,
  `Municipio` varchar(300) DEFAULT NULL,
  `Distrito` varchar(300) DEFAULT NULL,
  `Tipo_via` varchar(300) DEFAULT NULL,
  `Via` varchar(300) DEFAULT NULL,
  `LAT` varchar(45) DEFAULT NULL,
  `LON` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idLugar`),
  UNIQUE KEY `idLugar_UNIQUE` (`idLugar`)
) ENGINE=InnoDB AUTO_INCREMENT=144462 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plantilla_actuacion`
--

DROP TABLE IF EXISTS `plantilla_actuacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plantilla_actuacion` (
  `idPlantillaActuacion` int NOT NULL AUTO_INCREMENT,
  `Cod` varchar(45) DEFAULT NULL,
  `Unidad` varchar(300) DEFAULT NULL,
  `Jefatura` varchar(300) DEFAULT NULL,
  `Provincia` varchar(300) DEFAULT NULL,
  `Municipio` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`idPlantillaActuacion`)
) ENGINE=InnoDB AUTO_INCREMENT=143654 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `responsable`
--

DROP TABLE IF EXISTS `responsable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `responsable` (
  `Dni` varchar(45) NOT NULL,
  `Pais` varchar(45) DEFAULT NULL,
  `Edad` int DEFAULT NULL,
  `Sexo` varchar(45) DEFAULT NULL,
  `Municipio` varchar(45) DEFAULT NULL,
  `Nacionalidad` varchar(45) DEFAULT NULL,
  `Extranjeria` varchar(45) DEFAULT NULL,
  `Entrada_extranjero` varchar(45) DEFAULT NULL,
  `Detenciones` int DEFAULT NULL,
  PRIMARY KEY (`Dni`),
  UNIQUE KEY `Dni_UNIQUE` (`Dni`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `responsableshechos`
--

DROP TABLE IF EXISTS `responsableshechos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `responsableshechos` (
  `identificador_denuncia` varchar(100) NOT NULL,
  `id_responsable` varchar(45) NOT NULL,
  PRIMARY KEY (`identificador_denuncia`,`id_responsable`),
  KEY `Responsable_idx` (`id_responsable`),
  CONSTRAINT `Hecho` FOREIGN KEY (`identificador_denuncia`) REFERENCES `hecho` (`Identificador_denuncia`),
  CONSTRAINT `Responsable` FOREIGN KEY (`id_responsable`) REFERENCES `responsable` (`Dni`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tramo_horario`
--

DROP TABLE IF EXISTS `tramo_horario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tramo_horario` (
  `tramo_horario` varchar(30) NOT NULL,
  PRIMARY KEY (`tramo_horario`),
  UNIQUE KEY `tramo__horario_UNIQUE` (`tramo_horario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tramo_horario`
--

LOCK TABLES `tramo_horario` WRITE;
/*!40000 ALTER TABLE `tramo_horario` DISABLE KEYS */;
INSERT INTO `tramo_horario` VALUES ('Mañana'),('No informado'),('Noche'),('Tarde');
/*!40000 ALTER TABLE `tramo_horario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `usuario` varchar(100) NOT NULL,
  `contraseña` varchar(300) DEFAULT NULL,
  `administrador` tinyint DEFAULT NULL,
  `salt` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`usuario`),
  UNIQUE KEY `usuario_UNIQUE` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES ('admin','2daceebc4e31654d326ae7889b397ed50ff7e5afff374d1f89525865fd87efe0',1,'123456'),('usuario','4ec728b35075e859010bc42f3fe7eb31a9f406fe658c0f6b8a597f1bfcaf4fc9',0,'597413');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-10-06 19:23:46
