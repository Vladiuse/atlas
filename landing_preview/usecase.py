from .services import get_keitaro_landing_api_data, load_html_from_url
from .utils import get_keitaro_index_file_url, render_keitaro_landing_html
from .constants import KEITARO_PRODUCT_VAR_NAME, KEITARO_URL

class GetLandingHtmlWithProductUseCase:


    def execute(self, landing_id: str, product_name: str) -> str:
        kt_landing_data = get_keitaro_landing_api_data(landing_id=landing_id)
        landing_index_file_url = get_keitaro_index_file_url(landing_local_path=kt_landing_data['local_path'])
        html = load_html_from_url(url=landing_index_file_url)
        # with open("html.html", 'w') as file:
        #     file.write(html)
        # with open("html.html") as file:
        #     html = file.read()
        base_url = landing_index_file_url
        content = {
            KEITARO_PRODUCT_VAR_NAME: product_name,
        }
        return render_keitaro_landing_html(
            html=html,
            base_url=base_url,
            context=content,
        )


