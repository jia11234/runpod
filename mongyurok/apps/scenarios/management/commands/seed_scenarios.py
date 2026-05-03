"""
사용법: python manage.py seed_scenarios
"""
from django.core.management.base import BaseCommand
from apps.scenarios.models import SceneModeInfo, SceneChapter, SceneCharInfo


SCENARIO = dict(
    title="병자호란: 설한의 역습",
    summary=(
        "1636년 12월, 청나라 12만 대군이 압록강을 건넜다. "
        "도원수 김자점의 보고 누락으로 적 기병대는 이미 개성 코앞까지 진격한 "
        "절체절명의 상황. 당신은 조선을 구할 수 있는가?"
    ),
    keyword1="대체역사",
    keyword2="병자호란",
    default_personality="냉철하고 결단력 있는 책사. 위기 속에서도 이성을 잃지 않는다.",
    default_identity="조선의 신하이자 전략가. 임금 곁에서 나라의 운명을 함께 짊어진 인물.",
    default_values="백성을 지키는 것이 최우선. 명분과 실리 사이에서 최선의 길을 찾는다.",
    default_first_scene=(
        "1636년 12월, 한양 창덕궁 선정전. 피투성이가 된 파발마가 쓰러지며 외쳤다. "
        "'청나라 12만 대군이 압록강을 건넜습니다!' 전하의 얼굴이 새하얗게 질렸고, "
        "조정은 순식간에 아수라장이 되었다. 도원수 김자점의 보고 누락으로 "
        "적의 기병대는 이미 개성 코앞까지 진격해 있었다. "
        "남은 시간은 사흘. 당신은 무엇을 해야 하는가."
    ),
    # 대표 이미지: setup_media.py 실행 후 media/에 복사된 경로
    img_url="scenarios/byeongjahoran_main.png",
)

CHAPTERS = [
    dict(chapter_key="prologue", title="압록강의 파발, 골든타임의 시작", order=1,
         context_summary=(
             "때: 1636년 12월, 장소: 한양 창덕궁 선정전. "
             "청나라 12만 대군이 압록강을 도하했다는 보고가 들어왔다. "
             "도원수 김자점의 보고 누락으로 적 기병대는 이미 개성 코앞까지 진격한 상태. "
             "핵심 수치: time_remaining 초기값 3일. "
             "A안(결사대 파견): 성공 시 time_remaining +2, 실패 시 morale -15. "
             "B안(청야전술): food +30, 한양 인프라 파괴. "
             "C안(외교 기만): faction_split -20, loyalty +10."
         ),
         img_url="scenarios/backgrounds/prologue.png"),
    dict(chapter_key="act1", title="피 묻은 보급로", order=2,
         context_summary=(
             "때: 1636년 12월 중순, 장소: 남한산성 진입로 및 광주 일대. "
             "청군 선발대가 턱밑까지 추격해오는 가운데 최대한 많은 물자를 확보해야 한다. "
             "이벤트1[백성이냐 군량이냐]: loyalty +20, food -20 / food +20, loyalty -30, morale -10. "
             "이벤트2[검단산 탈환전]: 성공 시 food +25, morale +10 / 실패 시 morale -20. "
             "이 막에서 확보한 food 수치가 act2의 버티기 턴 수를 결정한다."
         ),
         img_url="scenarios/backgrounds/act1.png"),
    dict(chapter_key="act2", title="고립된 섬, 끓어오르는 가마솥", order=3,
         context_summary=(
             "때: 1636년 12월 하순~1637년 1월, 장소: 포위된 남한산성. "
             "food는 매 턴 -3씩 자동 감소. food=0이면 강제 배드엔딩. "
             "이벤트1[비밀 암문]: 성공 시 flags[밀서_전달]=true, morale +15 / 실패 시 morale -20. "
             "이벤트2[홍이포 사보타주]: 성공 시 flags[홍이포_파괴]=true, morale +20 / 실패 시 morale -25. "
             "이벤트3[심리전]: 성공 시 faction_split +10, time_remaining +1. "
             "faction_split이 -60 이하이면 최명길 주도 항복 루트 자동 트리거."
         ),
         img_url="scenarios/backgrounds/act2.png"),
    dict(chapter_key="act3", title="팔도의 깃발, 결전 또는 대담한 담판", order=4,
         context_summary=(
             "때: 포위 40일 차. flags[밀서_전달]=true이면 삼남 근왕군이 광주 인근에 결집. "
             "루트A[군사적 승리]: 조건 morale>=50, flags[밀서_전달]=true → 남한산성 대첩. "
             "루트B[외교적 승리]: 조건 flags[심리전]=true 또는 faction_split<0 → 형제 맹약 타협. "
             "루트A/B 모두 불가 시 배드엔딩 강제 진입."
         )),
    dict(chapter_key="epilogue", title="새로운 조선", order=5,
         context_summary=(
             "진엔딩[강철의 조선]: 루트A 성공. 삼전도 굴욕 없음. 조선 근대화 100년 앞당김. "
             "노멀엔딩[상처뿐인 평화]: 루트B 성공. 치욕은 피했으나 막대한 세공 부담. "
             "배드엔딩[역사의 반복]: food=0 또는 morale=0. 삼전도 굴욕, 유저 참수."
         )),
]

CHARACTERS = [
    # ── 메인 캐릭터 ──
    dict(name="인조",         is_extra=False,
         keyword="겁 많은 임금, 흔들리는 리더십",
         summary="결정적인 순간마다 망설이고 남을 잘 믿지 못하는 예민한 성격. 옆에서 중심을 잡아주지 않으면 최악의 선택을 내릴 수 있음.",
         img_url="scenarios/chars/byeongjahoran_injo.png"),
    dict(name="김자점",       is_extra=False,
         keyword="자기밖에 모르는 빌런, 무능한 대장님",
         summary="나라가 망하든 자기 밥그릇 챙기기에 바쁜 인물. 적군 침입 보고도 씹어버릴 만큼 무책임하며 거짓말을 밥 먹듯 함.",
         img_url="scenarios/chars/byeongjahoran_kimjajeom.png"),
    dict(name="최명길",       is_extra=False,
         keyword="욕먹어도 고(GO)! 현실적인 브레인",
         summary="일단 살고 봐야 한다는 현실주의자. 비겁하다는 비난을 들어도 나라를 지키기 위해 치욕을 감수하려 함. 주화파의 핵심.",
         img_url="scenarios/chars/byeongjahoran_choimyunggil.png"),
    dict(name="김상헌",       is_extra=False,
         keyword="대나무 같은 선비, 원칙주의 끝판왕",
         summary="죽어도 굽힐 수 없다는 강한 자존심의 소유자. 병사들의 사기를 올리는 정신적 지주. 척화파의 핵심.",
         img_url="scenarios/chars/byeongjahoran_kimsangheon.png"),
    dict(name="청 태종 숭덕제", is_extra=False,
         keyword="조선의 숨통을 쥐고 있는 냉혹한 정복자",
         summary="청나라를 세운 강력한 황제. 압도적 군사력과 홍이포로 끊임없이 압박하는 최종 보스.",
         img_url="scenarios/chars/byeongjahoran_chongtaejong.png"),
    # ── 엑스트라 ──
    dict(name="남한산성 포졸", is_extra=True,
         keyword=None,
         summary="남한산성을 지키는 일반 병사. 굶주림과 추위 속에서도 자리를 지키고 있다.",
         img_url="scenarios/chars/byeongjahoran_pojol.png"),
    dict(name="피난처 할머니", is_extra=True,
         keyword=None,
         summary="전란을 피해 산성 안으로 들어온 노인. 백성들의 처지를 대변하는 인물.",
         img_url="scenarios/chars/byeongjahoran_halmoni.png"),
    dict(name="청나라 사신",   is_extra=True,
         keyword=None,
         summary="청 태종의 명을 받아 항복을 요구하러 오는 인물. 오만하고 위압적인 태도로 협박한다.",
         img_url=None),
]


class Command(BaseCommand):
    help = "병자호란 시나리오 초기 데이터를 DB에 삽입합니다."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="기존 병자호란 시나리오를 삭제하고 새로 삽입합니다.")

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = SceneModeInfo.objects.filter(title=SCENARIO["title"]).delete()
            self.stdout.write(self.style.WARNING(f"기존 시나리오 삭제 (연관 포함): {deleted}개"))

        # 1. 시나리오
        scene, created = SceneModeInfo.objects.get_or_create(
            title=SCENARIO["title"],
            defaults={k: v for k, v in SCENARIO.items() if k != "title"},
        )

        if not created:
            self.stdout.write(self.style.WARNING(
                f"⏭️  이미 존재: {scene.title}  (--reset으로 재삽입 가능)"
            ))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ 시나리오 생성: {scene.title}"))

        # 2. 챕터
        self.stdout.write("\n[챕터]")
        for ch in CHAPTERS:
            SceneChapter.objects.create(scene=scene, **ch)
            self.stdout.write(f"  ✅ {ch['order']}. {ch['title']}")

        # 3. 등장인물
        self.stdout.write("\n[등장인물]")
        for char in CHARACTERS:
            SceneCharInfo.objects.create(scene=scene, **char)
            role = "엑스트라" if char["is_extra"] else "메인"
            self.stdout.write(f"  ✅ [{role}] {char['name']}")

        self.stdout.write(self.style.SUCCESS(
            f"\n완료 — 챕터 {len(CHAPTERS)}개 / 캐릭터 {len(CHARACTERS)}개 삽입됨"
        ))
