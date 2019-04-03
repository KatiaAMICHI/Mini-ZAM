let rec h(x,y)= if x<0 then y else h(x-1, y+1)

let f x = h(x, 0)

let _ = f 2
