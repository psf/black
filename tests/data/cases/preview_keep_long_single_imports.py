# flags: --preview --line-length=56
from company.product.department.project.handlers import register
from .product.department.project.handlers import (register as register_handler)
from company.product.department.project.handlers import register, unregister
from company.product.department.project.handlers import (register,)
from company.product.department.project.handlers import (
    # Keep the comment inside the import.
    register
)
from company.product.department.project.handlers import register  # noqa: F401

# output
from company.product.department.project.handlers import register
from .product.department.project.handlers import register as register_handler
from company.product.department.project.handlers import (
    register,
    unregister,
)
from company.product.department.project.handlers import (
    register,
)
from company.product.department.project.handlers import (
    # Keep the comment inside the import.
    register,
)
from company.product.department.project.handlers import (
    register,
)  # noqa: F401
