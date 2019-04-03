let rec insert x l =
  match l with
  | [] -> [x]
  | y::ys -> y::(insert x ys)

let rec insert_sqr l =
    match l with
    | [] -> []
    | x::xs -> let a = x*x in insert a (insert_sqr xs)

let _ = insert_sqr [1;2;1;1;1]
