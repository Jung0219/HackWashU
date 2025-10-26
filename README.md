# HackWashU
HackWashU 10/24/2025 ~ 10/26/2025

## AI-Powered Healthcare Price Transparency Advisor
Seyun Jeong, Isabelle Cox, Gihwan Jung, Nilesh Gupta

### Abstract
The AI-Powered Healthcare Price Transparency Navigator (TransparAI) is a platform that integrates real-time computer vision with hospital price transparency. It guides users in classifying wound images and comparing local costs, helping patients find affordable care and make informed decisions, thus promoting collaboration between people and AI for social good.

### User Experience
The system is user-centric, requiring only a wound photo and zip code entry + non-invasive insurance information. The interface provides intuitive, side-by-side, real world hospital price comparisons, highlighting cost savings for each provider. Results are presented clearly, offering users quick and actionable insights.

<img width="605" height="451" alt="Screenshot 2025-10-26 at 8 36 14 AM" src="https://github.com/user-attachments/assets/f06bb25e-e85f-4682-979d-bd689d244c26" />

### Functional Prototype
The working demo first classifies a wound type given an image using a custom-trained deep neural network model. Given this wound type, the software then maps it to standard billing codes and instantly queries a real-time database of hospital service prices. The backend efficiently processes data using a Flask REST API, compressing gigabyte-scale datasets into rapid, user-facing lookups. Users can test the platform’s full functionality, from image upload to price comparison and insurance cost estimation.

### Impact and Scalability
Empowering patients with data-driven price transparency, our platform lets users estimate wound care costs instantly and privately—no cloud uploads needed. Leveraging AI classification and real CMS data, patients can save up to 93% per case, and typical abrasion-related procedures show real-world savings of $58 per patient, scaling to $58,000 across 1,000 users. Our network spans 4,000 hospitals and 71,000 procedures, with expansion-ready architecture for other medical services. Patients with common insurance plans (e.g., $500 deductible, 90% coverage, $50 copay) can save up to $2,000 per surgical negotiation—totaling $2 million for 1,000 users. Fully compliant with federal transparency regulations, this solution is built for nationwide impact.

<img width="278" height="509" alt="Screenshot 2025-10-26 at 8 35 55 AM" src="https://github.com/user-attachments/assets/cfc737c3-e1ae-4fbd-854c-4688eab9e3e0" />
