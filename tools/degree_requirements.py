"""
Degree and concentration requirements data for Chicago Booth MBA.
These are returned as tool results to Claude — no LLM call needed,
just structured text that Claude interprets.
"""

DEGREE_REQUIREMENTS = """
MBA Degree Requirements — Booth School of Business

REQUIRED COURSES (one each):
  Financial Accounting: 30000, 30116, 30120, 30122, 30130, 30131
  Microeconomics: 33001, 33002, 33101, ECON 30100, ECON 30200
  Statistics: 41000, 41100, 41201, 41202, 41203, 41204, 41206, 41207, 41301, 41305, 41813, 41814, 41901, 41902, 41903, 41910, 41916

FUNCTIONS/LEADERSHIP ELECTIVES — complete 7 of the following 8:
  Finance:     35000, 35001, 35200 (foundations); electives: 34101, 34901-34904, 35100, 35120, 35130, 35150, 35201, 35210, 35214
  Marketing:   37000, 37110 (foundations); electives: 37101, 37103, 37105-37107, 37200-37202, 37208-37209, 37301, 37304, 37703, 37704
  Operations:  40000 (foundation); electives: 40101, 40108, 40110
  Strategy:    42001 (foundation); electives: 39001, 39101, 42116, 42135, 42715
  Decisions:   30005, 30001, 36106, 38002, 38120, 36109
  People:      33032, 38001, 38003, 39002 (foundations); electives: 31403, 38122
  Economy:     33050, 33040, 33112 (foundations); electives: 33401, 33403, 33501-33503, 33520
  Society:     33305, 33471, 37212, 38119 (foundations); electives: 30133, 33251, 34113, 34117, 38115, 38126, 42201
"""

CONCENTRATION_REQUIREMENTS = """
Chicago Booth MBA Concentrations (optional, noted on transcript)

Accounting: 400 units from: 30000, 30005/30001, 30116, 30118, 30120, 30121, 30122, 30130, 30131, 30132, 30133, 30135, 30830, 30835, 30840

Behavioral Science: 400 units from: 31403, 31702, 38001-38003, 38101-38107, 38115-38120, 38122-38123, 38126, 38820-38821, 38825, 38865, 38870, 38875, 38886, 39002

Business Analytics:
  - 100 units data science: 41201 or 41204
  - 100 units decision models: 36106 or 36109
  - 300 units electives from: 30135, 32100-32130, 32200-32210, 36109, 37103, 37105, 37107, 37202, 40108, 40206, 41201-41204, 41301, 41305, 41814

Business, Society & Sustainability: 400 units from:
  - Social Sector: 34113, 34115, 34117, 42125, 42710, 42711
  - Corporate Citizenship/ESG: 30133, 31425, 37212, 38112, 42708
  - Role of Business: 33305, 33251+33250, 35225, 42129
  - Ethics: 38119, 33471, 38115, 38128

Econometrics & Statistics: 300 units from: 41000, 41100, 41201-41204, 41206/41813, 41207, 41301/41305, 41813-41814, 41901-41903, 41910

Economics: 400 units from: 33032, 33050/33040, 33101, 33112, 33222, 33230, 33251+33250, 33301, 33305, 33350, 33401, 33403, 33454, 33501-33503, 33520, 33882, 38120, 42001, 42116, 42135 (NOT 33001 or 33002)

Entrepreneurship: 300 units from: 30118, 30121, 31401-31403, 34101-34108, 34111, 34113, 34115, 34117, 34205-34210, 34211, 34219-34220, 34302, 34305-34306, 34702, 34704-34705, 34709, 34715, 34815-34816, 34820, 34825-34826, 34880, 34887-34888, 35123, 35213, 35823, 36110, 36820, 37200-37201, 37301, 37703, 39101, 40110, 41206/41813, 41301/41305, 41813, 42705, 42711, 42820

Finance:
  - 100 units asset pricing: 34901, 34902, 35000, 35100, 35101, 35120-35121, 35126, 35130-35132, 35901, 35908
  - 100 units corporate finance: 34101, 34903-34904, 35200-35202, 35210, 35213-35215
  - 200 units electives from extended finance list

Analytic Finance: 600 units from: 34101, 34901-34904, 35100, 35120-35121, 35126, 35130-35133, 35150, 35200-35202, 35210, 35213-35215, 35219, 35901, 35907-35908, 41203

General Management: All 8 lines (800 units) of Functions/Leadership requirements + 300 units from strategic management or behavioral science

Healthcare: 400 units; at least 100 from 33350, 40206/40205; 200-300 from 33351-33352, 34205, 34210, 42300, 42310; up to 100 experiential units

International Business: 300 units from: 30131, 33501-33503, 33520, 35210, 35213, 35219 (must include 33501 or 33502)

Marketing Management: 37000/37110 + 300 units from: 37101, 37103/37105, 37107, 37110, 37200-37202, 37208-37209, 37212, 37301, 37703, 37810, 37816, 37882, 37902, 41301/41305

Operations Management: 300 units from: 36106, 36109, 40000, 40101, 40108, 40110, 40111, 40206/40205, 40721, 40810-40811

Strategic Management: 300 units from: 33222, 39001, 39101, 42001, 42116, 42125, 42129, 42135, 42708, 42711, 42715, 42820
"""


def get_degree_requirements(query: str) -> str:
    """Return the full degree requirements text for Claude to reason over."""
    return f"""Here are the Booth MBA degree requirements:

{DEGREE_REQUIREMENTS}

Student's question: {query}
"""


def get_concentration_requirements(query: str) -> str:
    """Return the full concentration requirements text for Claude to reason over."""
    return f"""Here are the Booth MBA concentration requirements:

{CONCENTRATION_REQUIREMENTS}

Student's question: {query}
"""
