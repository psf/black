# flags: --minimum-version=3.12
def many_type_params[Alpha, Beta, Gamma, Delta, Epsilon, Zeta, Eta, Theta, Iota, Kappa](x): pass


def bound_overflow[TypeVariableWithABound: SomeVeryLongBoundExpressionThatWontFitOnOneLineAtAll](x): pass


def constraint_overflow[T: (FirstConstraint, SecondConstraint, ThirdConstraint, FourthConstraint)](x): pass


def params_and_args_overflow[TypeParamOne, TypeParamTwo, TypeParamThree](argument_one: int, argument_two: str, argument_three: bytes) -> ReturnType: pass


def return_type_overflow[T](x: T) -> SomeVeryLongReturnTypeAnnotationThatForcesTheReturnAnnotationToWrapAround[T]: pass


type LongAlias[TypeParamOne, TypeParamTwo, TypeParamThree] = dict[TypeParamOne, tuple[TypeParamTwo, TypeParamThree]]


class GenericClass[TypeParameterOne, TypeParameterTwo, TypeParameterThree](BaseOne, BaseTwo, metaclass=Meta): pass


def nested_generic[T](x: Mapping[str, Sequence[tuple[T, VeryLongTypeNameGoesHere, AnotherLongOne]]]) -> None: pass

# output

def many_type_params[Alpha, Beta, Gamma, Delta, Epsilon, Zeta, Eta, Theta, Iota, Kappa](
    x,
):
    pass


def bound_overflow[
    TypeVariableWithABound: SomeVeryLongBoundExpressionThatWontFitOnOneLineAtAll
](
    x,
):
    pass


def constraint_overflow[
    T: (FirstConstraint, SecondConstraint, ThirdConstraint, FourthConstraint)
](
    x,
):
    pass


def params_and_args_overflow[TypeParamOne, TypeParamTwo, TypeParamThree](
    argument_one: int, argument_two: str, argument_three: bytes
) -> ReturnType:
    pass


def return_type_overflow[T](
    x: T,
) -> SomeVeryLongReturnTypeAnnotationThatForcesTheReturnAnnotationToWrapAround[T]:
    pass


type LongAlias[TypeParamOne, TypeParamTwo, TypeParamThree] = dict[
    TypeParamOne, tuple[TypeParamTwo, TypeParamThree]
]


class GenericClass[TypeParameterOne, TypeParameterTwo, TypeParameterThree](
    BaseOne, BaseTwo, metaclass=Meta
):
    pass


def nested_generic[T](
    x: Mapping[str, Sequence[tuple[T, VeryLongTypeNameGoesHere, AnotherLongOne]]],
) -> None:
    pass
