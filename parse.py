import ast
import dis
import sys
from pathlib import Path

def parse_file_to_ast(file_path: str) -> ast.Module:
    """
    读取Python文件并将其解析为AST
    :param file_path: Python文件路径
    :return: AST模块对象
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content)
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    except SyntaxError as e:
        print(f"语法错误: {e}")
        sys.exit(1)

def print_ast(ast_obj: ast.Module, indent: int = 0) -> None:
    """
    以缩进形式打印AST
    :param ast_obj: AST对象
    :param indent: 缩进级别
    """
    prefix = '  ' * indent
    print(f"{prefix}{type(ast_obj).__name__}")
    
    # 处理AST节点的属性
    for attr in dir(ast_obj):
        if not attr.startswith('_') and attr not in {'lineno', 'col_offset', 'end_lineno', 'end_col_offset'}:
            value = getattr(ast_obj, attr)
            if not callable(value):
                if isinstance(value, list):
                    if value and all(isinstance(item, ast.AST) for item in value):
                        print(f"{prefix}  {attr}:")
                        for item in value:
                            print_ast(item, indent + 2)
                elif isinstance(value, ast.AST):
                    print(f"{prefix}  {attr}:")
                    print_ast(value, indent + 2)
                else:
                    print(f"{prefix}  {attr}: {value}")

def compile_to_bytecode(file_path: str) -> None:
    """
    编译Python文件并打印字节码
    :param file_path: Python文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = compile(f.read(), file_path, 'exec')
        dis.dis(code)
    except Exception as e:
        print(f"编译错误: {e}")
        sys.exit(1)

def main():
    """
    主函数：解析命令行参数并处理文件
    """
    if len(sys.argv) != 2:
        print("用法: python ast_bytecode_parser.py <python_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).is_file() or not file_path.endswith('.py'):
        print(f"错误: '{file_path}' 不是有效的Python文件")
        sys.exit(1)
    
    print(f"解析文件: {file_path}\n")
    
    # 解析为AST
    print("=== AST结构 ===")
    ast_tree = parse_file_to_ast(file_path)
    print_ast(ast_tree)
    
    print("\n\n=== 字节码 ===")
    compile_to_bytecode(file_path)

if __name__ == "__main__":
    main()    
