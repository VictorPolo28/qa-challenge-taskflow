#!/usr/bin/env python3
"""
Seed Script — Populates the database with realistic test data.
Run: python seed.py [--api-url http://localhost:8080]
"""

import argparse
import json
import sys
import time
import requests

DEFAULT_URL = "http://localhost:8080/api"

USERS = [
    {
        "username": "jperez",
        "email": "juan.perez@empresa.com",
        "full_name": "Juan Pérez García",
        "role": "admin"
    },
    {
        "username": "mlopez",
        "email": "maria.lopez@empresa.com",
        "full_name": "María López Martínez",
        "role": "member"
    },
    {
        "username": "crodriguez",
        "email": "carlos.rodriguez@empresa.com",
        "full_name": "Carlos Rodríguez Sánchez",
        "role": "member"
    },
    {
        "username": "agonzalez",
        "email": "ana.gonzalez@empresa.com",
        "full_name": "Ana González Fernández",
        "role": "manager"
    },
    {
        "username": "fmartinez",
        "email": "francisco.martinez@empresa.com",
        "full_name": "Francisco Martínez Ruiz",
        "role": "member"
    },
    {
        "username": "lsanchez",
        "email": "laura.sanchez@empresa.com",
        "full_name": "Laura Sánchez Díaz",
        "role": "member"
    },
    {
        "username": "dramirez",
        "email": "diego.ramirez@empresa.com",
        "full_name": "Diego Ramírez Torres",
        "role": "admin"
    },
    {
        "username": "ctorres",
        "email": "carmen.torres@empresa.com",
        "full_name": "Carmen Torres Flores",
        "role": "member"
    },
    {
        "username": "rflores",
        "email": "roberto.flores@empresa.com",
        "full_name": "Roberto Flores Mendoza",
        "role": "member"
    },
    {
        "username": "gcastro",
        "email": "gabriela.castro@empresa.com",
        "full_name": "Gabriela Castro Reyes",
        "role": "manager"
    },
    {
        "username": "avalencia",
        "email": "alejandro.valencia@empresa.com",
        "full_name": "Alejandro Valencia Ortiz",
        "role": "member"
    },
    {
        "username": "mreyes",
        "email": "martha.reyes@empresa.com",
        "full_name": "Martha Reyes Jiménez",
        "role": "member"
    },
    {
        "username": "jguerrero",
        "email": "jorge.guerrero@empresa.com",
        "full_name": "Jorge Guerrero Vega",
        "role": "admin"
    },
    {
        "username": "snavarro",
        "email": "sofia.navarro@empresa.com",
        "full_name": "Sofía Navarro Paredes",
        "role": "member"
    },
    {
        "username": "lmedina",
        "email": "luis.medina@empresa.com",
        "full_name": "Luis Medina Cordero",
        "role": "member"
    },
    {
        "username": "pvargas",
        "email": "patricia.vargas@empresa.com",
        "full_name": "Patricia Vargas Guzmán",
        "role": "manager"
    },
    {
        "username": "aherrera",
        "email": "andres.herrera@empresa.com",
        "full_name": "Andrés Herrera Campos",
        "role": "member"
    },
    {
        "username": "ecampos",
        "email": "elena.campos@empresa.com",
        "full_name": "Elena Campos Ríos",
        "role": "member"
    },
    {
        "username": "vromero",
        "email": "victor.romero@empresa.com",
        "full_name": "Víctor Romero Acosta",
        "role": "admin"
    },
    {
        "username": "nsoto",
        "email": "nadia.soto@empresa.com",
        "full_name": "Nadia Soto Pacheco",
        "role": "member"
    },
    {
        "username": "icruz",
        "email": "ivan.cruz@empresa.com",
        "full_name": "Iván Cruz Molina",
        "role": "member"
    },
    {
        "username": "blara",
        "email": "beatriz.lara@empresa.com",
        "full_name": "Beatriz Lara Núñez",
        "role": "manager"
    },
    {
        "username": "esilva",
        "email": "esteban.silva@empresa.com",
        "full_name": "Esteban Silva Carrasco",
        "role": "member"
    },
    {
        "username": "mrojas",
        "email": "monica.rojas@empresa.com",
        "full_name": "Mónica Rojas Bustos",
        "role": "member"
    },
    {
        "username": "gvillarreal",
        "email": "guillermo.villarreal@empresa.com",
        "full_name": "Guillermo Villarreal Peña",
        "role": "admin"
    },
    {
        "username": "taguirre",
        "email": "teresita.aguirre@empresa.com",
        "full_name": "Teresita Aguirre Fuentes",
        "role": "member"
    },
    {
        "username": "ocardenas",
        "email": "oscar.cardenas@empresa.com",
        "full_name": "Óscar Cárdenas Salinas",
        "role": "member"
    },
    {
        "username": "lzuniga",
        "email": "lorena.zuniga@empresa.com",
        "full_name": "Lorena Zúñiga Espinoza",
        "role": "manager"
    },
    {
        "username": "hsalgado",
        "email": "hugo.salgado@empresa.com",
        "full_name": "Hugo Salgado Miranda",
        "role": "member"
    },
    {
        "username": "mperalta",
        "email": "miriam.peralta@empresa.com",
        "full_name": "Miriam Peralta Godoy",
        "role": "member"
    },
    {
        "username": "cibarra",
        "email": "cesar.ibarra@empresa.com",
        "full_name": "César Ibarra Figueroa",
        "role": "admin"
    },
    {
        "username": "yavila",
        "email": "yanet.avila@empresa.com",
        "full_name": "Yanet Ávila Montes",
        "role": "member"
    },
    {
        "username": "rparedes",
        "email": "raul.paredes@empresa.com",
        "full_name": "Raúl Paredes Cáceres",
        "role": "member"
    },
    {
        "username": "mvaldes",
        "email": "macarena.valdes@empresa.com",
        "full_name": "Macarena Valdés Tapia",
        "role": "manager"
    },
    {
        "username": "efuentes",
        "email": "enrique.fuentes@empresa.com",
        "full_name": "Enrique Fuentes Carrillo",
        "role": "member"
    },
    {
        "username": "ncortes",
        "email": "nicolas.cortes@empresa.com",
        "full_name": "Nicolás Cortes Vega",
        "role": "member"
    },
    {
        "username": "valarcon",
        "email": "valeria.alarcon@empresa.com",
        "full_name": "Valeria Alarcón Rivera",
        "role": "admin"
    },
    {
        "username": "fvillanueva",
        "email": "felipe.villanueva@empresa.com",
        "full_name": "Felipe Villanueva Mora",
        "role": "member"
    },
    {
        "username": "cescobar",
        "email": "claudia.escobar@empresa.com",
        "full_name": "Claudia Escobar Duarte",
        "role": "member"
    },
    {
        "username": "hsandoval",
        "email": "hector.sandoval@empresa.com",
        "full_name": "Héctor Sandoval Pizarro",
        "role": "manager"
    },
    {
        "username": "mbarraza",
        "email": "manuel.barraza@empresa.com",
        "full_name": "Manuel Barraza Sepúlveda",
        "role": "member"
    },
    {
        "username": "cquiroz",
        "email": "catalina.quiroz@empresa.com",
        "full_name": "Catalina Quiroz Palma",
        "role": "member"
    },
    {
        "username": "sserrano",
        "email": "sebastian.serrano@empresa.com",
        "full_name": "Sebastián Serrano Calvo",
        "role": "admin"
    },
    {
        "username": "mpoblete",
        "email": "marcela.poblete@empresa.com",
        "full_name": "Marcela Poblete Uribe",
        "role": "member"
    },
    {
        "username": "gbravo",
        "email": "german.bravo@empresa.com",
        "full_name": "Germán Bravo Araneda",
        "role": "member"
    },
    {
        "username": "jvillegas",
        "email": "josefina.villegas@empresa.com",
        "full_name": "Josefina Villegas Osses",
        "role": "manager"
    },
    {
        "username": "fzamora",
        "email": "francisca.zamora@empresa.com",
        "full_name": "Francisca Zamora Leiva",
        "role": "member"
    },
    {
        "username": "asantibanez",
        "email": "arturo.santibanez@empresa.com",
        "full_name": "Arturo Santibáñez Gajardo",
        "role": "member"
    },
    {
        "username": "dmoreno",
        "email": "daniela.moreno@empresa.com",
        "full_name": "Daniela Moreno Carrera",
        "role": "admin"
    },
    {
        "username": "rjimenez",
        "email": "rodrigo.jimenez@empresa.com",
        "full_name": "Rodrigo Jiménez Gallegos",
        "role": "member"
    },
    {
        "username": "mbarrientos",
        "email": "marisol.barrientos@empresa.com",
        "full_name": "Marisol Barrientos Aravena",
        "role": "member"
    },
    {
        "username": "cparedes",
        "email": "cristian.paredes@empresa.com",
        "full_name": "Cristian Paredes Venegas",
        "role": "manager"
    },
    {
        "username": "vvergara",
        "email": "viviana.vergara@empresa.com",
        "full_name": "Viviana Vergara Cifuentes",
        "role": "member"
    },
    {
        "username": "econtreras",
        "email": "eduardo.contreras@empresa.com",
        "full_name": "Eduardo Contreras Loyola",
        "role": "member"
    },
    {
        "username": "mmanriquez",
        "email": "miguel.manriquez@empresa.com",
        "full_name": "Miguel Manríquez Valenzuela",
        "role": "admin"
    },
    {
        "username": "pbustamante",
        "email": "pablo.bustamante@empresa.com",
        "full_name": "Pablo Bustamante Olguín",
        "role": "member"
    },
    {
        "username": "cmiranda",
        "email": "constanza.miranda@empresa.com",
        "full_name": "Constanza Miranda Gutiérrez",
        "role": "member"
    },
    {
        "username": "janriquez",
        "email": "javier.anriquez@empresa.com",
        "full_name": "Javier Anríquez Parra",
        "role": "manager"
    },
    {
        "username": "tgarrido",
        "email": "tomas.garrido@empresa.com",
        "full_name": "Tomás Garrido Saavedra",
        "role": "member"
    },
    {
        "username": "nrojas",
        "email": "natalia.rojas@empresa.com",
        "full_name": "Natalia Rojas Pereira",
        "role": "member"
    },
    {
        "username": "pferreira",
        "email": "patricio.ferreira@empresa.com",
        "full_name": "Patricio Ferreira Riquelme",
        "role": "admin"
    },
    {
        "username": "cmella",
        "email": "camila.mella@empresa.com",
        "full_name": "Camila Mella Carvajal",
        "role": "member"
    },
    {
        "username": "aovalle",
        "email": "andrea.ovalle@empresa.com",
        "full_name": "Andrea Ovalle Zamora",
        "role": "member"
    },
    {
        "username": "lbadilla",
        "email": "luis.badilla@empresa.com",
        "full_name": "Luis Badilla Henríquez",
        "role": "manager"
    },
    {
        "username": "mcaamano",
        "email": "marco.caamano@empresa.com",
        "full_name": "Marco Caamaño Azócar",
        "role": "member"
    },
    {
        "username": "fmaureira",
        "email": "fabiola.maureira@empresa.com",
        "full_name": "Fabiola Maureira Oyarzo",
        "role": "member"
    },
    {
        "username": "cbarra",
        "email": "cristobal.barra@empresa.com",
        "full_name": "Cristóbal Barra Jara",
        "role": "admin"
    },
    {
        "username": "mzuñiga",
        "email": "macarena.zuniga@empresa.com",
        "full_name": "Macarena Zúñiga Hormazábal",
        "role": "member"
    },
    {
        "username": "rorellana",
        "email": "renato.orellana@empresa.com",
        "full_name": "Renato Orellana Basualto",
        "role": "member"
    },
    {
        "username": "jmunoz",
        "email": "jessica.munoz@empresa.com",
        "full_name": "Jessica Muñoz Cárdenas",
        "role": "manager"
    },
    {
        "username": "fburgos",
        "email": "francisco.burgos@empresa.com",
        "full_name": "Francisco Burgos Yañez",
        "role": "member"
    },
    {
        "username": "paraya",
        "email": "paulina.araya@empresa.com",
        "full_name": "Paulina Araya Gatica",
        "role": "member"
    },
    {
        "username": "areyes",
        "email": "ariel.reyes@empresa.com",
        "full_name": "Ariel Reyes Marchant",
        "role": "admin"
    },
    {
        "username": "molivares",
        "email": "marisol.olivares@empresa.com",
        "full_name": "Marisol Olivares Cuevas",
        "role": "member"
    },
    {
        "username": "jvega",
        "email": "julio.vega@empresa.com",
        "full_name": "Julio Vega Donoso",
        "role": "member"
    },
    {
        "username": "kperez",
        "email": "karla.perez@empresa.com",
        "full_name": "Karla Pérez Fuenzalida",
        "role": "manager"
    },
    {
        "username": "avarela",
        "email": "angel.varela@empresa.com",
        "full_name": "Ángel Varela Catalan",
        "role": "member"
    },
    {
        "username": "ggodoy",
        "email": "gabriel.godoy@empresa.com",
        "full_name": "Gabriel Godoy Espinoza",
        "role": "member"
    },
    {
        "username": "cruiz",
        "email": "clara.ruiz@empresa.com",
        "full_name": "Clara Ruiz Lagos",
        "role": "admin"
    },
    {
        "username": "mbascunan",
        "email": "matias.bascunan@empresa.com",
        "full_name": "Matías Bascuñán Pereira",
        "role": "member"
    },
    {
        "username": "idiaz",
        "email": "ignacio.diaz@empresa.com",
        "full_name": "Ignacio Díaz Salazar",
        "role": "member"
    },
    {
        "username": "clagos",
        "email": "carlos.lagos@empresa.com",
        "full_name": "Carlos Lagos Mondaca",
        "role": "manager"
    },
    {
        "username": "avivanco",
        "email": "alejandra.vivanco@empresa.com",
        "full_name": "Alejandra Vivanco Sepúlveda",
        "role": "member"
    },
    {
        "username": "jcerda",
        "email": "juan.cerda@empresa.com",
        "full_name": "Juan Cerda Fuentes",
        "role": "member"
    },
    {
        "username": "psanhueza",
        "email": "paola.sanhueza@empresa.com",
        "full_name": "Paola Sanhueza Neira",
        "role": "admin"
    },
    {
        "username": "pzapata",
        "email": "pedro.zapata@empresa.com",
        "full_name": "Pedro Zapata Inostroza",
        "role": "member"
    },
    {
        "username": "mgarrido",
        "email": "marcela.garrido@empresa.com",
        "full_name": "Marcela Garrido Navarro",
        "role": "member"
    },
    {
        "username": "fretamal",
        "email": "felipe.retamal@empresa.com",
        "full_name": "Felipe Retamal Vera",
        "role": "manager"
    },
    {
        "username": "cvergara",
        "email": "carolina.vergara@empresa.com",
        "full_name": "Carolina Vergara Figueroa",
        "role": "member"
    },
    {
        "username": "rgallardo",
        "email": "rodrigo.gallardo@empresa.com",
        "full_name": "Rodrigo Gallardo Pinto",
        "role": "member"
    },
    {
        "username": "mbaeza",
        "email": "mario.baeza@empresa.com",
        "full_name": "Mario Baeza Opazo",
        "role": "admin"
    },
    {
        "username": "jleiva",
        "email": "josefina.leiva@empresa.com",
        "full_name": "Josefina Leiva Salas",
        "role": "member"
    },
    {
        "username": "raguilera",
        "email": "rodrigo.aguilera@empresa.com",
        "full_name": "Rodrigo Aguilera Abarca",
        "role": "member"
    },
    {
        "username": "vgaete",
        "email": "valentina.gaete@empresa.com",
        "full_name": "Valentina Gaete Barrera",
        "role": "manager"
    },
    {
        "username": "hulloa",
        "email": "humberto.ulloa@empresa.com",
        "full_name": "Humberto Ulloa Medel",
        "role": "member"
    },
    {
        "username": "mcañas",
        "email": "marcos.cañas@empresa.com",
        "full_name": "Marcos Cañas Acuña",
        "role": "member"
    },
    {
        "username": "fbustos",
        "email": "francisca.bustos@empresa.com",
        "full_name": "Francisca Bustos Ruiz",
        "role": "admin"
    },
    {
        "username": "lcaceres",
        "email": "luis.caceres@empresa.com",
        "full_name": "Luis Cáceres Morales",
        "role": "member"
    },
    {
        "username": "acabrera",
        "email": "andrea.cabrera@empresa.com",
        "full_name": "Andrea Cabrera Valdivia",
        "role": "member"
    },
    {
        "username": "escobar",
        "email": "eduardo.scobar@empresa.com",
        "full_name": "Eduardo Scobar Toledo",
        "role": "manager"
    },
    {
        "username": "cfaundez",
        "email": "carla.faundez@empresa.com",
        "full_name": "Carla Faúndez Manríquez",
        "role": "member"
    },
    {
        "username": "jibanez",
        "email": "jose.ibanez@empresa.com",
        "full_name": "José Ibáñez Zavala",
        "role": "member"
    },
    {
        "username": "nvillegas",
        "email": "nicole.villegas@empresa.com",
        "full_name": "Nicole Villegas Jofré",
        "role": "admin"
    },
    {
        "username": "rpalma",
        "email": "ricardo.palma@empresa.com",
        "full_name": "Ricardo Palma Vergara",
        "role": "member"
    },
    {
        "username": "mflores",
        "email": "marcela.flores@empresa.com",
        "full_name": "Marcela Flores Montoya",
        "role": "member"
    },
    {
        "username": "garaya",
        "email": "gonzalo.araya@empresa.com",
        "full_name": "Gonzalo Araya Hermosilla",
        "role": "manager"
    },
    {
        "username": "psoto",
        "email": "pamela.soto@empresa.com",
        "full_name": "Pamela Soto Valenzuela",
        "role": "member"
    },
    {
        "username": "lvera",
        "email": "luis.vera@empresa.com",
        "full_name": "Luis Vera Guajardo",
        "role": "member"
    },
    {
        "username": "ctoro",
        "email": "cristina.toro@empresa.com",
        "full_name": "Cristina Toro Cancino",
        "role": "admin"
    },
    {
        "username": "fvidal",
        "email": "francisco.vidal@empresa.com",
        "full_name": "Francisco Vidal Castro",
        "role": "member"
    },
    {
        "username": "myevenez",
        "email": "macarena.yevenez@empresa.com",
        "full_name": "Macarena Yévenez Rivas",
        "role": "member"
    },
    {
        "username": "jmora",
        "email": "jorge.mora@empresa.com",
        "full_name": "Jorge Mora Alvarado",
        "role": "manager"
    },
    {
        "username": "csilva",
        "email": "camila.silva@empresa.com",
        "full_name": "Camila Silva Pino",
        "role": "member"
    },
    {
        "username": "ffarias",
        "email": "fernando.farias@empresa.com",
        "full_name": "Fernando Farías Saldivia",
        "role": "member"
    },
    {
        "username": "mleticia",
        "email": "maria.leticia@empresa.com",
        "full_name": "María Leticia Cuevas",
        "role": "admin"
    },
    {
        "username": "acifuentes",
        "email": "alfredo.cifuentes@empresa.com",
        "full_name": "Alfredo Cifuentes Mardones",
        "role": "member"
    },
    {
        "username": "vmanosalva",
        "email": "victoria.manosalva@empresa.com",
        "full_name": "Victoria Manosalva Lagos",
        "role": "member"
    },
    {
        "username": "gmiranda",
        "email": "gustavo.miranda@empresa.com",
        "full_name": "Gustavo Miranda Loyola",
        "role": "manager"
    },
    {
        "username": "msanhueza",
        "email": "monica.sanhueza@empresa.com",
        "full_name": "Mónica Sanhueza Pereira",
        "role": "member"
    },
    {
        "username": "chidalgo",
        "email": "cristian.hidalgo@empresa.com",
        "full_name": "Cristian Hidalgo Muñoz",
        "role": "member"
    },
    {
        "username": "loyarce",
        "email": "lorena.oyarce@empresa.com",
        "full_name": "Lorena Oyarce Fuentes",
        "role": "admin"
    },
    {
        "username": "jvasquez",
        "email": "juan.vasquez@empresa.com",
        "full_name": "Juan Vásquez Espinoza",
        "role": "member"
    },
    {
        "username": "mcornejo",
        "email": "marcela.cornejo@empresa.com",
        "full_name": "Marcela Cornejo Rojas",
        "role": "member"
    },
    {
        "username": "rfernandez",
        "email": "rodrigo.fernandez@empresa.com",
        "full_name": "Rodrigo Fernández Cartes",
        "role": "manager"
    },
    {
        "username": "pmella",
        "email": "paula.mella@empresa.com",
        "full_name": "Paula Mella Aburto",
        "role": "member"
    },
    {
        "username": "fvalladares",
        "email": "francisco.valladares@empresa.com",
        "full_name": "Francisco Valladares Briones",
        "role": "member"
    },
    {
        "username": "ahormazabal",
        "email": "andrea.hormazabal@empresa.com",
        "full_name": "Andrea Hormazábal Garrido",
        "role": "admin"
    },
    {
        "username": "jsanhueza",
        "email": "javier.sanhueza@empresa.com",
        "full_name": "Javier Sanhueza Valdés",
        "role": "member"
    },
    {
        "username": "cpavez",
        "email": "constanza.pavez@empresa.com",
        "full_name": "Constanza Pavez Ulloa",
        "role": "member"
    },
    {
        "username": "pcalderon",
        "email": "pedro.calderon@empresa.com",
        "full_name": "Pedro Calderón Catalán",
        "role": "manager"
    },
    {
        "username": "mcarvajal",
        "email": "maria.carvajal@empresa.com",
        "full_name": "María Carvajal Leiva",
        "role": "member"
    },
    {
        "username": "jborquez",
        "email": "jose.borquez@empresa.com",
        "full_name": "José Bórquez Salazar",
        "role": "member"
    },
    {
        "username": "curra",
        "email": "catalina.urra@empresa.com",
        "full_name": "Catalina Urra Mondaca",
        "role": "admin"
    },
    {
        "username": "lsaldivia",
        "email": "luis.saldivia@empresa.com",
        "full_name": "Luis Saldivia Peña",
        "role": "member"
    },
    {
        "username": "francino",
        "email": "fernanda.rancino@empresa.com",
        "full_name": "Fernanda Francino López",
        "role": "member"
    },
    {
        "username": "rcuevas",
        "email": "roberto.cuevas@empresa.com",
        "full_name": "Roberto Cuevas Vera",
        "role": "manager"
    },
    {
        "username": "mvivanco",
        "email": "marcela.vivanco@empresa.com",
        "full_name": "Marcela Vivanco Farías",
        "role": "member"
    },
    {
        "username": "jpinilla",
        "email": "juan.pinilla@empresa.com",
        "full_name": "Juan Pinilla Zamorano",
        "role": "member"
    },
    {
        "username": "chuenchuman",
        "email": "carla.huenchuman@empresa.com",
        "full_name": "Carla Huenchumán Catrileo",
        "role": "admin"
    },
    {
        "username": "fpino",
        "email": "francisco.pino@empresa.com",
        "full_name": "Francisco Pino Cerda",
        "role": "member"
    },
    {
        "username": "gvallejos",
        "email": "gabriela.vallejos@empresa.com",
        "full_name": "Gabriela Vallejos Silva",
        "role": "member"
    },
    {
        "username": "ccalderara",
        "email": "carlos.calderara@empresa.com",
        "full_name": "Carlos Calderara Miranda",
        "role": "manager"
    },
    {
        "username": "mvillegas",
        "email": "manuel.villegas@empresa.com",
        "full_name": "Manuel Villegas Carrasco",
        "role": "member"
    },
    {
        "username": "esepulveda",
        "email": "evelyn.sepulveda@empresa.com",
        "full_name": "Evelyn Sepúlveda Rojas",
        "role": "member"
    },
    {
        "username": "ibarra",
        "email": "ignacio.barra@empresa.com",
        "full_name": "Ignacio Barra Cataldo",
        "role": "admin"
    },
    {
        "username": "jcaroca",
        "email": "jorge.caroca@empresa.com",
        "full_name": "Jorge Caroca Bravo",
        "role": "member"
    },
    {
        "username": "cmatus",
        "email": "carolina.matus@empresa.com",
        "full_name": "Carolina Matus Galaz",
        "role": "member"
    },
    {
        "username": "aranquil",
        "email": "andrea.ranquil@empresa.com",
        "full_name": "Andrea Ranquil Paillal",
        "role": "manager"
    },
    {
        "username": "galvarado",
        "email": "gonzalo.alvarado@empresa.com",
        "full_name": "Gonzalo Alvarado Tapia",
        "role": "member"
    },
    {
        "username": "freinoso",
        "email": "fabiola.reinoso@empresa.com",
        "full_name": "Fabiola Reinoso González",
        "role": "member"
    },
    {
        "username": "lmorales",
        "email": "luis.morales@empresa.com",
        "full_name": "Luis Morales Díaz",
        "role": "admin"
    },
    {
        "username": "ccancino",
        "email": "claudia.cancino@empresa.com",
        "full_name": "Claudia Cancino Muñoz",
        "role": "member"
    },
    {
        "username": "pvilches",
        "email": "pablo.vilches@empresa.com",
        "full_name": "Pablo Vilches Molina",
        "role": "member"
    },
    {
        "username": "nrodriguez",
        "email": "nicolas.rodriguez@empresa.com",
        "full_name": "Nicolás Rodríguez Flores",
        "role": "manager"
    },
    {
        "username": "mvidal",
        "email": "maria.vidal@empresa.com",
        "full_name": "María Vidal Fonseca",
        "role": "member"
    },
    {
        "username": "cvergara2",
        "email": "cristobal.vergara@empresa.com",
        "full_name": "Cristóbal Vergara Leal",
        "role": "member"
    },
    {
        "username": "jguzman",
        "email": "javier.guzman@empresa.com",
        "full_name": "Javier Guzmán Palma",
        "role": "admin"
    },
    {
        "username": "tvillegas",
        "email": "tamara.villegas@empresa.com",
        "full_name": "Tamara Villegas Gutiérrez",
        "role": "member"
    },
    {
        "username": "fleon",
        "email": "francisco.leon@empresa.com",
        "full_name": "Francisco León Bustos",
        "role": "member"
    },
    {
        "username": "amarileo",
        "email": "andrea.marileo@empresa.com",
        "full_name": "Andrea Marileo Huenchual",
        "role": "manager"
    },
    {
        "username": "cmillapan",
        "email": "carlos.millapan@empresa.com",
        "full_name": "Carlos Millapán Curín",
        "role": "member"
    },
    {
        "username": "pmanque",
        "email": "paula.manque@empresa.com",
        "full_name": "Paula Manque Lefimil",
        "role": "member"
    },
    {
        "username": "fneculman",
        "email": "fernando.neculman@empresa.com",
        "full_name": "Fernando Neculman Melinao",
        "role": "admin"
    }
]

PROJECTS = [
    {"name": "Portal Web Corporativo", "description": "Rediseño del portal web principal de la empresa"},
    {"name": "App Móvil v2", "description": "Segunda versión de la aplicación móvil para clientes"},
    {"name": "Migración Cloud", "description": "Migración de infraestructura on-premise a AWS"},
]

TASKS = [
    # Portal Web
    {"title": "Diseñar wireframes de la página de inicio", "description": "Crear wireframes de baja fidelidad para la nueva página de inicio del portal", "priority": "high", "status": "done", "tags": ["diseño", "frontend"], "due_date": "2025-12-15"},
    {"title": "Implementar sistema de autenticación OAuth", "description": "Integrar login con Google y Microsoft usando OAuth 2.0", "priority": "critical", "status": "in_progress", "tags": ["backend", "seguridad"], "due_date": "2026-03-10"},
    {"title": "Optimizar queries de la página de reportes", "description": "Las queries del dashboard de reportes toman más de 5 segundos. Optimizar con índices y caching.", "priority": "high", "status": "in_review", "tags": ["backend", "performance"], "due_date": "2026-03-05"},
    {"title": "Corregir responsive del menú de navegación", "description": "El menú hamburguesa no funciona en iOS Safari", "priority": "medium", "status": "todo", "tags": ["frontend", "bug"], "due_date": "2026-03-20"},
    {"title": "Escribir tests e2e para flujo de registro", "description": "Cubrir el flujo completo de registro de usuario con Playwright", "priority": "medium", "status": "todo", "tags": ["testing", "frontend"], "due_date": "2026-04-01"},
    {"title": "Configurar CDN para assets estáticos", "description": None, "priority": "low", "status": "todo", "tags": ["infra"], "due_date": None},
    {"title": "Actualizar dependencias de seguridad", "description": "npm audit muestra 3 vulnerabilidades high. Actualizar packages.", "priority": "critical", "status": "todo", "tags": ["seguridad", "mantenimiento"], "due_date": "2026-02-28"},

    # App Móvil
    {"title": "Implementar push notifications", "description": "Integrar Firebase Cloud Messaging para notificaciones push en Android e iOS", "priority": "high", "status": "in_progress", "tags": ["mobile", "backend"], "due_date": "2026-03-15"},
    {"title": "Diseñar pantalla de onboarding", "description": "3 pantallas de bienvenida con animaciones Lottie", "priority": "medium", "status": "done", "tags": ["diseño", "mobile"], "due_date": "2025-11-30"},
    {"title": "Fix crash en Android 14 al abrir cámara", "description": "La app crash con NullPointerException al intentar abrir la cámara en dispositivos Samsung con Android 14", "priority": "critical", "status": "in_progress", "tags": ["bug", "mobile", "android"], "due_date": "2026-03-01"},
    {"title": "Implementar modo offline", "description": "Cachear datos críticos con Room DB para funcionamiento sin conexión", "priority": "high", "status": "todo", "tags": ["mobile", "backend"], "due_date": "2026-04-15"},
    {"title": "Tests de rendimiento en dispositivos low-end", "description": "Verificar performance en Moto G4 y similares. Target: 60fps en scroll, <2s cold start.", "priority": "medium", "status": "todo", "tags": ["testing", "performance"], "due_date": "2026-04-30"},

    # Migración Cloud
    {"title": "Documentar arquitectura actual on-premise", "description": "Diagrama de todos los servicios, bases de datos, y dependencias actuales", "priority": "high", "status": "done", "tags": ["documentación", "infra"], "due_date": "2025-10-15"},
    {"title": "Configurar VPC y subnets en AWS", "description": "VPC con subnets públicas y privadas en 2 AZs. NAT Gateway para salida de subnets privadas.", "priority": "critical", "status": "done", "tags": ["infra", "aws"], "due_date": "2025-12-01"},
    {"title": "Migrar base de datos PostgreSQL a RDS", "description": "Migrar la BD principal (500GB) usando DMS con mínimo downtime", "priority": "critical", "status": "in_review", "tags": ["infra", "aws", "database"], "due_date": "2026-03-20"},
    {"title": "Configurar monitoring con CloudWatch", "description": "Dashboards para CPU, memoria, disco, latencia de API, y error rates", "priority": "high", "status": "todo", "tags": ["infra", "monitoring"], "due_date": "2026-04-10"},
    {"title": "Plan de disaster recovery", "description": "Documentar RPO/RTO y procedimientos de recovery para cada servicio crítico", "priority": "medium", "status": "todo", "tags": ["documentación", "infra"], "due_date": "2026-05-01"},
    {"title": "Configurar alertas de costos", "description": "Budget alerts en AWS cuando el gasto exceda $5000/mes", "priority": "low", "status": "cancelled", "tags": ["infra", "aws"], "due_date": None},
]


def seed(api_url):
    print(f"\n🌱 Seeding data to {api_url}...\n")

    # Wait for API
    for i in range(10):
        try:
            r = requests.get(f"{api_url}/health", timeout=3)
            if r.status_code == 200:
                break
        except:
            pass
        print(f"  Waiting for API... ({i+1}/10)")
        time.sleep(2)
    else:
        print("❌ API not available")
        sys.exit(1)

    # Create users
    user_ids = []
    print("👤 Creating users...")
    for u in USERS:
        r = requests.post(f"{api_url}/users", json=u)
        if r.status_code == 201:
            user_ids.append(r.json()["id"])
            print(f"   ✓ {u['full_name']}")
        else:
            print(f"   ✗ {u['username']}: {r.text}")
            user_ids.append(None)

    # Create projects
    project_ids = []
    print("\n📁 Creating projects...")
    for i, p in enumerate(PROJECTS):
        p["owner_id"] = user_ids[0]  # admin owns all
        r = requests.post(f"{api_url}/projects", json=p)
        if r.status_code == 201:
            project_ids.append(r.json()["id"])
            print(f"   ✓ {p['name']}")
        else:
            print(f"   ✗ {p['name']}: {r.text}")
            project_ids.append(None)

    # Create tasks
    print("\n📝 Creating tasks...")
    task_project_map = [0]*7 + [1]*5 + [2]*6  # distribute tasks across projects
    for i, t in enumerate(TASKS):
        proj_idx = task_project_map[i] if i < len(task_project_map) else 0
        task_data = {
            "title": t["title"],
            "description": t.get("description"),
            "project_id": project_ids[proj_idx],
            "assignee_id": user_ids[(i % 4) + 1],  # rotate assignees (skip admin)
            "reporter_id": user_ids[0],
            "priority": t["priority"],
            "due_date": t.get("due_date"),
            "tags": t.get("tags", []),
        }
        r = requests.post(f"{api_url}/tasks", json=task_data)
        if r.status_code == 201:
            task_id = r.json()["id"]
            # Update status if not 'todo'
            if t["status"] != "todo":
                requests.put(f"{api_url}/tasks/{task_id}", json={"status": t["status"]})
            print(f"   ✓ {t['title'][:60]}...")
        else:
            print(f"   ✗ {t['title'][:40]}: {r.text}")

    print(f"\n✅ Seed complete! Created {len(USERS)} users, {len(PROJECTS)} projects, {len(TASKS)} tasks.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed TaskFlow with test data")
    parser.add_argument("--api-url", default=DEFAULT_URL, help="API base URL")
    args = parser.parse_args()
    seed(args.api_url)
