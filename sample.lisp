(begin
    (define r 10)
    (warp-by 0 (* -1 r))
    (loop-upto i 360 ( begin (move (* r (sin (/ tau 360)))) (turn 1) ))
    (warp-by 0 r)
    (turn 45)
    (move (* 50 (sqrt 2)))
    (warp-by -40 -40)
    (turn -3)
    (loop-upto i 4 ( begin (move (if (= 0 (% i 2)) 15 22)) (turn 90)))
)
