import os
import sys
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

def render_template(template_name, context):
    # Establish absolute path to the templates directory
    templates_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates")

    # Initialize Jinja2 environment with strict variable enforcement
    env = Environment(
        loader=FileSystemLoader(templates_path),
        undefined=StrictUndefined
    )

    # Retrieve the requested template file
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        raise FileNotFoundError(f"Template '{template_name}' not found in templates directory")

    # Generate the final output using the provided data context
    try:
        return template.render(context)
    except Exception as e:
        raise RuntimeError(f"Error rendering template '{template_name}': {e}")