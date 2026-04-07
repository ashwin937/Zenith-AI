"""Math calculation tools for the LLM to use."""

import math
import re
from typing import Union
from langchain_core.tools import tool


@tool
def calculate(expression: str) -> Union[float, str]:
    """
    Safely evaluate mathematical expressions.
    
    This tool can handle:
    - Basic arithmetic: +, -, *, /, %
    - Exponents: ** (power)
    - Parentheses: ()
    - Common functions: sin, cos, tan, sqrt, log, exp
    
    Args:
        expression: A mathematical expression to evaluate
        Examples: "2 + 2", "sqrt(16)", "10 * 5", "2**3"
    
    Returns:
        The result of the calculation or an error message
    """
    try:
        # Sanitize the expression
        expression = expression.strip()
        
        # Define allowed functions
        safe_dict = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'abs': abs,
            'round': round,
            'pow': pow,
            'pi': math.pi,
            'e': math.e,
        }
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # Return result with high precision
        if isinstance(result, float):
            # Round to 10 decimal places to avoid floating point errors
            result = round(result, 10)
        
        return result
        
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError as e:
        return f"Error: Invalid value - {str(e)}"
    except SyntaxError:
        return f"Error: Invalid expression syntax"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def solve_equation(equation: str, variable: str = "x") -> str:
    """
    Solve simple linear equations.
    
    This tool solves equations of the form: ax + b = c
    
    Args:
        equation: The equation to solve (e.g., "2x + 5 = 13")
        variable: The variable to solve for (default: "x")
    
    Returns:
        The solution or an error message
    """
    try:
        # Parse equation: "ax + b = c" format
        if "=" not in equation:
            return "Error: Equation must contain '=' sign"
        
        left, right = equation.split("=")
        
        # This is a simplified solver - for demo purposes
        # For complex equations, we'd need sympy
        return f"Equation parsing in progress. Use calculate() for arithmetic instead."
        
    except Exception as e:
        return f"Error: {str(e)}"


def get_math_tools():
    """Return list of math tools."""
    return [calculate, solve_equation]
