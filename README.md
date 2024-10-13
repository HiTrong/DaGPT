# DaGPT

[![Python](https://img.shields.io/badge/3.10-green?style=flat-square&logo=Python&label=Python&labelColor=green&color=grey)](https://www.python.org/downloads/release/python-3100/)
[![PyTorch](https://img.shields.io/badge/11.8-black?style=flat-square&logo=Torch&logoColor=red&label=Torch&labelColor=orange&color=grey)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/tokenizers-black?style=flat-square&logo=HuggingFace&logoColor=red&label=HuggingFace&labelColor=yellow&color=grey)](https://pypi.org/project/tokenizers/)
[![Gemini API](https://img.shields.io/badge/Free_API-black?style=flat-square&logo=Google&logoColor=white&label=Gemini&labelColor=blue&color=grey)](https://pypi.org/project/tokenizers/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Application-red?logo=Streamlit&logoColor=Red&labelColor=white)](https://docs.streamlit.io/)
[![Apache 2.0 License](https://img.shields.io/badge/Apache_2.0-blue?style=flat-square&logo=License&logoColor=red&label=License&labelColor=blue&color=grey)](https://www.apache.org/licenses/LICENSE-2.0)

Với mục tiêu xây dựng một **chatbot** tư vấn trả lời câu hỏi về **da liễu** dựa trên mô hình ngôn ngữ lớn, chúng ta sẽ tiến hành một số bước như sau:

| Giai đoạn | Thao tác |
|-----------|----------|
| Giai đoạn 1 | Tìm kiếm và thu thập các nguồn dữ liệu uy tín (Web crawling, dữ liệu từ bộ y tế) |
| Giai đoạn 2 | Tăng cường dữ liệu và sinh dữ liệu tổng hợp thông qua API Gemini |
| Giai đoạn 3 | Tiền xử lý và hợp nhất dữ liệu |
| Giai đoạn 4 | Xây dựng bộ Tokenizer |
| Giai đoạn 5 | Thử nghiệm và tối ưu hóa kiến trúc mô hình, khối lượng dữ liệu cùng với tài nguyên phần cứng hỗ trợ miễn trên Kaggle |
| Giai đoạn 6 | Huấn luyện trước mô hình (pretrain) |
| Giai đoạn 7 | Tinh chỉnh mô hình cho bài toán trả lời câu hỏi |
| Giai đoạn 8 | Tích hợp mô hình vào ứng dụng chatbot streamlit |

## 📄 Giai đoạn 1, 2, 3: Chuẩn bị dữ liệu

- Các nguồn dữ liệu được chúng tôi thu thập từ các trang web uy tín bao gồm: các bài viết, hội thảo, tư vấn trả lời online, từ điển bệnh lý,... Ngoài ra còn có dữ liệu từ bộ y tế: [Hướng dẫn chuẩn đoán điều trị da liễu](https://kcb.vn/upload/2005611/20210723/Huong-dan-chan-doan-dieu-tri-Da-lieu.pdf)

- Đối với dữ liệu của bộ y tế, chúng tôi sẽ sử dụng kỹ thuật **Data Augmentation** và **Synthetic Data Generation** để gia tăng lượng dữ liệu cũng đa dạng hóa ngữ cảnh. **Gemini** là một trong những mô hình ngôn ngữ lớn nổi tiếng và mạnh mẽ nhất hiện tại. Ngoài ra **Google AI Studio** còn hỗ trợ API cho một số mô hình trong nhánh **Gemini**. Tận dụng những điều đó, chúng tôi tiến hành **prompting** cũng như xây dựng một pipeline để tăng cường và sinh dữ liệu tổng hợp dựa trên mô hình ngôn ngữ lớn mạnh mẽ đó. Đầu tiên ta sẽ trích xuất thông tin từ file **PDF** và trong giai đoạn này sẽ có một số hiện tượng như sai phông chữ, hoặc thông tin không rõ ràng, ta sẽ tiến hành yêu cầu mô hình sửa chửa đoạn thông tin đó và tiếp tục thực hiện các nhiệm vụ **Data Augmentation** và **Synthetic Data Generation**. Cuối cùng ta sẽ đưa dữ liệu vào một file **CSV** hoặc **TXT**. Để dễ hiểu, Pipeline được thể hiện như sau:

![Data Augmentation & Synthetic Data Generation Pipeline](/Data%20Augmentation%20and%20Synthetic/pipeline_img.png)

- Cuối cùng, dữ liệu được nhiều nguồn sẽ được làm sạch cơ bản như:
> - Loại bỏ giá trị null, rỗng, giá trị duplicate
> - Loại bỏ các thông tin gây nhiễu: link, url, các kí tự kéo dài (ví dụ: ................, --------------,..., \n\n\n\n, !!!, ???)
> - Loại bỏ các thông tin gây vi phạm chính sách người dùng, tổ chức: tên tổ chức, email, sđt,...

- **Kết quả:** Dữ liệu được hợp nhất và chia dữ liệu ra thành tập train và tập test (Bao gồm 4 files)
