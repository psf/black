# flags: --unstable --minimum-version=3.13
def func[*Ts = Set["ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"]]():
    pass

def func[**P = Set["ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"]]():
    pass

class Class[*Ts = Set["ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"]]:
    pass

type Alias[**P = Set["ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"]] = int

# output

def func[
    *Ts = Set[
        "ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar |"
        " AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"
    ]
]():
    pass


def func[
    **P = Set[
        "ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar |"
        " AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"
    ]
]():
    pass


class Class[
    *Ts = Set[
        "ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar |"
        " AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"
    ]
]:
    pass


type Alias[
    **P = Set[
        "ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar |"
        " AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"
    ]
] = int
