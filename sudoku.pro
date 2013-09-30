:- use_module(library(clpfd)).

% shorthand for printing the solution of problem X
sud(O) :-
  open(O, write, OF),
  problem(1, Rows), sudoku(Rows), maplist(write(OF), Rows),
  close(OF).

% sudoku solving:
sudoku(Rows) :-
  % Rows is a list of the list Vs
  % where Vs contains values from 1 to 9
  append(Rows, Vs), Vs ins 1..9,
  % all values in the lists in Rows have to be distinct
  maplist(all_distinct, Rows),
  % split up Rows into Columns and check them
  transpose(Rows, Columns), maplist(all_distinct, Columns),
  % check the blocks
  Rows = [A,B,C,D,E,F,G,H,I],
  blocks(A, B, C), blocks(D, E, F), blocks(G, H, I),
  % force a definite value for every variable in Rows
  maplist(label, Rows).

blocks([], [], []).
blocks([A,B,C|Bs1], [D,E,F|Bs2], [G,H,I|Bs3]) :-
  % all values in a block are distinct
  all_distinct([A,B,C,D,E,F,G,H,I]),
  blocks(Bs1, Bs2, Bs3).
