% ============================================================
% FAMILY KNOWLEDGE BASE - DYNAMIC RULES ONLY (NO FACTS)
% ============================================================
% In Unit 2, facts are dynamically learned at runtime from 
% user natural language input and appended to this file.
% ============================================================

% ---------- RULES (30+) ----------

% 1. father(X, Y): X is father of Y
father(X, Y) :- male(X), parent(X, Y).

% 2. mother(X, Y): X is mother of Y
mother(X, Y) :- female(X), parent(X, Y).

% 3. son(X, Y): X is son of Y
son(X, Y) :- male(X), parent(Y, X).

% 4. daughter(X, Y): X is daughter of Y
daughter(X, Y) :- female(X), parent(Y, X).

% 5. child(X, Y): X is a child of Y
child(X, Y) :- parent(Y, X).

% 6. grandparent(X, Y): X is grandparent of Y
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).

% 7. grandfather(X, Y): X is grandfather of Y
grandfather(X, Y) :- male(X), grandparent(X, Y).

% 8. grandmother(X, Y): X is grandmother of Y
grandmother(X, Y) :- female(X), grandparent(X, Y).

% 9. grandchild(X, Y): X is grandchild of Y
grandchild(X, Y) :- grandparent(Y, X).

% 10. grandson(X, Y): X is grandson of Y
grandson(X, Y) :- male(X), grandchild(X, Y).

% 11. granddaughter(X, Y): X is granddaughter of Y
granddaughter(X, Y) :- female(X), grandchild(X, Y).

% 12. sibling(X, Y): X and Y are siblings (share at least one parent)
sibling(X, Y) :- parent(Z, X), parent(Z, Y).

% 13. brother(X, Y): X is a brother of Y
brother(X, Y) :- male(X), sibling(X, Y).

% 14. sister(X, Y): X is a sister of Y
sister(X, Y) :- female(X), sibling(X, Y).

% 15. husband(X, Y): X is husband of Y
husband(X, Y) :- married(X, Y).

% 16. wife(X, Y): X is wife of Y
wife(X, Y) :- married(Y, X).

% 17. spouse(X, Y): X and Y are spouses
spouse(X, Y) :- married(X, Y).
spouse(X, Y) :- married(Y, X).

% 18. uncle(X, Y): X is uncle of Y
uncle(X, Y) :- male(X), sibling(X, Z), parent(Z, Y).

% 19. aunt(X, Y): X is aunt of Y
aunt(X, Y) :- female(X), sibling(X, Z), parent(Z, Y).

% 20. nephew(X, Y): X is nephew of Y
nephew(X, Y) :- male(X), uncle(Y, X).

% 21. niece(X, Y): X is niece of Y
niece(X, Y) :- female(X), aunt(Y, X).

% 22. cousin(X, Y): X and Y are cousins
cousin(X, Y) :- parent(Z, X), parent(W, Y), sibling(Z, W).

% 23. ancestor(X, Y): X is an ancestor of Y
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% 24. descendant(X, Y): X is a descendant of Y
descendant(X, Y) :- ancestor(Y, X).

% 25. father_in_law(X, Y): X is father-in-law of Y
father_in_law(X, Y) :- male(X), spouse(Y, Z), parent(X, Z).

% 26. mother_in_law(X, Y): X is mother-in-law of Y
mother_in_law(X, Y) :- female(X), spouse(Y, Z), parent(X, Z).

% 27. son_in_law(X, Y): X is son-in-law of Y
son_in_law(X, Y) :- male(X), parent(Y, Z), spouse(Z, X).

% 28. daughter_in_law(X, Y): X is daughter-in-law of Y
daughter_in_law(X, Y) :- female(X), parent(Y, Z), spouse(Z, X).

% 29. brother_in_law(X, Y): X is brother-in-law of Y
brother_in_law(X, Y) :- male(X), spouse(Y, Z), sibling(X, Z).
brother_in_law(X, Y) :- male(X), sibling(Y, Z), spouse(Z, X).

% 30. sister_in_law(X, Y): X is sister-in-law of Y
sister_in_law(X, Y) :- female(X), spouse(Y, Z), sibling(X, Z).
sister_in_law(X, Y) :- female(X), sibling(Y, Z), spouse(Z, X).

% 31. older_than(X, Y): X is older than Y based on DoB year
older_than(X, Y) :- dob(X, DX), dob(Y, DY), DX < DY.

% 32. younger_than(X, Y): X is younger than Y
younger_than(X, Y) :- older_than(Y, X).

% 33. same_generation(X, Y): X and Y share the same generation
same_generation(X, Y) :- sibling(X, Y).
same_generation(X, Y) :- cousin(X, Y).

% 34. has_children(X): X has at least one child
has_children(X) :- parent(X, Y).

% 35. is_married(X): X is currently married
is_married(X) :- married(X, Y).
is_married(X) :- married(Y, X).

male(ali).
parent(fatima, hassan).
female(fatima).
parent(ali, hassan).
parent(ali, sana).
parent(fatima, sana).
male(hassan).
parent(hassan, usman).
female(ayesha).
parent(ayesha, usman).
male(omar).
parent(omar, bilal).
female(sana).
parent(sana, bilal).
