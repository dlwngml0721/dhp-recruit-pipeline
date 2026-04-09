"""
Figma MCP 기반 이미지 생성 모듈.

흐름:
1. Figma MCP(use_figma)로 template 복제
2. variable 텍스트 레이어 수정
3. 프레임 이름을 기업명으로 설정
4. 사용자에게 Figma 데스크톱에서 Export 안내

※ Figma 플러그인 샌드박스 제한으로 로컬 파일 저장은 불가.
  Export는 사용자가 Figma 데스크톱에서 직접 수행.
"""

# Figma 파일 정보
FIGMA_FILE_KEY = "byXx50MB9bSu1x6bqjWmla"
TEMPLATE_NODE_ID = "1:2"


def generate_figma_plugin_code(company: str, category: str, position: str) -> str:
    """
    Figma Plugin API 코드를 생성합니다.
    Claude Code에서 use_figma 도구로 실행하세요.

    Args:
        company: 기업명 (예: "탑헬스") — 프레임 이름으로 사용
        category: 기업 종류 (예: "건강기능식품 브랜드")
        position: 포지션 종류 (예: "웹 콘텐츠 디자이너")

    Returns:
        Figma Plugin API JavaScript 코드 문자열
    """
    variable_text = f"({category} / {position})"

    return f"""
const template = figma.getNodeById("{TEMPLATE_NODE_ID}");
if (!template) return {{ success: false, error: "template not found" }};

const clone = template.clone();
clone.name = "{company}";
clone.x = template.x + 1200;

function findTextNode(node) {{
  if (node.type === "TEXT" && node.name === "variable") return node;
  if ("children" in node) {{
    for (const child of node.children) {{
      const found = findTextNode(child);
      if (found) return found;
    }}
  }}
  return null;
}}

const variableNode = findTextNode(clone);
if (!variableNode) {{
  clone.remove();
  return {{ success: false, error: "variable node not found" }};
}}

await figma.loadFontAsync({{ family: "Noto Sans KR", style: "Bold" }});
variableNode.fontName = {{ family: "Noto Sans KR", style: "Bold" }};
variableNode.characters = "{variable_text}";

figma.viewport.scrollAndZoomIntoView([clone]);

return {{ success: true, cloneId: clone.id, name: clone.name }};
"""
