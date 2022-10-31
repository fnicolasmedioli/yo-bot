% Introduccion a la Programacion I
materia(6111, 1, 1).
% Analisis Matematico I
materia(6112, 1, 1).
% Algebra I
materia(6113, 1, 1).
% Quimica
materia(6114, 1, 1).
% Ciencias de la Computacion I
materia(6121, 1, 2).
% Introduccion a la Programacion II
materia(6122, 1, 2).
% Algebra Lineal
materia(6123, 1, 2).
% Fisica General
materia(6124, 1, 2).
% Matematica Discreta
materia(6125, 1, 2).
% Ciencias de la Computacion II
materia(6211, 2, 1).
% Analisis y Diseno de Algoritmos I
materia(6212, 2, 1).
% Introduccion a la Arquitectura de Sistemas
materia(6213, 2, 1).
% Analisis Matematico II
materia(6214, 2, 1).
% Electricidad y Magnetismo
materia(6215, 2, 1).
% Analisis y Diseno de Algoritmos II
materia(6221, 2, 2).
% Comunicacion de Datos I
materia(6222, 2, 2).
% Probabilidades y Estadistica
materia(6223, 2, 2).
% Programacion Orientada a Objetos
materia(6311, 3, 1).
% Estructuras de Almacenamiento de Datos
materia(6312, 3, 1).
% Metodologias de Desarrollo de Software I
materia(6313, 3, 1).
% Electronica Digital
materia(6224, 2, 2).
% Ingles
materia(9001, 2, 2).
% Arquitectura de Computadoras I
materia(6314, 3, 1).
% Programacion Exploratoria
materia(6321, 3, 2).
% Base de Datos I
materia(6322, 3, 2).
% Lenguajes de Programacion I
materia(6323, 3, 2).
% Sistemas Operativos I
materia(6324, 3, 2).
% Investigacion Operativa I
materia(6325, 3, 2).
% Arquitectura de Computadoras y Tecnicas Digitales
materia(6411, 4, 1).
% Teoria de la Informacion
materia(6412, 4, 1).
% Comunicacion de Datos II
materia(6413, 4, 1).
% Introduccion al Calculo Diferencial e Integral
materia(6414, 4, 1).
% Diseno de Sistemas de Software
materia(6421, 4, 2).
% Diseno de Compiladores I
materia(6422, 4, 2).
% Ingenieria de Software
materia(6511, 5, 1).

nota_cursada(6111, 6.5).
nota_cursada(6114, 7.2).
nota_cursada(6121, 10).
nota_cursada(6123, 5).
nota_cursada(6125, 6).
nota_cursada(6211, 7).
nota_cursada(6212, 7).
nota_cursada(6214, 8.5).
nota_cursada(6215, 7).
nota_cursada(6313, 7).
nota_cursada(6312, 5).
nota_cursada(6311, 7).
nota_cursada(6221, 6.5).
nota_cursada(6222, 8).

nota_final(6111, 8).
nota_final(6114, 5.8).
nota_final(6121, 10).
nota_final(6123, 7).
nota_final(6125, 5).
nota_final(6211, 9.5).
nota_final(6212, 5.5).
nota_final(6214, 4).
nota_final(6222, 6.5).

nota_promocion(6112, 7.5).
nota_promocion(6113, 8).
nota_promocion(6122, 8.5).
nota_promocion(6124, 7).
nota_promocion(6213, 8.67).
nota_promocion(6223, 7.2).

en_curso(6323).
en_curso(6322).
en_curso(6325).
en_curso(6321).
en_curso(9001).
en_curso(6224).

me_gusta(6311). % Objetos
me_gusta(6215). % Electricidad
me_gusta(6321). % Exploratoria
me_gusta(6322). % Bases de Datos
me_gusta(6212). % Ayda 1
me_gusta(6221). % Ayda 2
me_gusta(9001). % Ingles
me_gusta(6224). % Electronica

materia_adeudada(X) :- materia(X, _, _), nota_cursada(X, _), not(nota_final(X, _)).
materia_de(Codigo, Anio) :- materia(Codigo, Anio, _).

estado_asignatura(Codigo, Resultado) :- nota_promocion(Codigo, _), Resultado = 'promocion'.
estado_asignatura(Codigo, Resultado) :- nota_final(Codigo, _), Resultado = 'examen'.
estado_asignatura(Codigo, Resultado) :- nota_cursada(Codigo, _), Resultado = 'cursada'.
estado_asignatura(Codigo, Resultado) :- en_curso(Codigo), Resultado = 'en curso'.
estado_asignatura(_, Resultado) :- Resultado = 'no cursada'.