"""
사용법: python manage.py seed_characters
"""
from django.core.management.base import BaseCommand
from apps.characters.models import CharModeInfo


CHARACTERS = [
    dict(kor_name="태조",   hanja_name="太祖",   birth_to_death="1335-1408",
         keyword1="건국",    keyword2="개혁",    keyword3="결단력",
         summary="조선을 건국한 초대 왕으로 강력한 리더십과 결단력을 보유.",
         img_url="characters/taejo.jpg"),
    dict(kor_name="태종",   hanja_name="太宗",   birth_to_death="1367-1422",
         keyword1="왕권강화", keyword2="냉철함",  keyword3="정치력",
         summary="강력한 왕권 확립과 정치적 결단으로 조선의 기틀을 다진 왕.",
         img_url="characters/taejong.png"),
    dict(kor_name="세종",   hanja_name="世宗",   birth_to_death="1397-1450",
         keyword1="훈민정음", keyword2="애민정신", keyword3="과학기술",
         summary="백성을 위해 훈민정음을 창제하고 과학기술 발전을 이끈 성군.",
         img_url="characters/sejong.jpg"),
    dict(kor_name="세조",   hanja_name="世祖",   birth_to_death="1417-1468",
         keyword1="쿠데타",  keyword2="권력",    keyword3="실용주의",
         summary="왕위를 찬탈했지만 이후 국가 운영 능력을 보인 왕.",
         img_url="characters/sejo.jpg"),
    dict(kor_name="성종",   hanja_name="成宗",   birth_to_death="1457-1494",
         keyword1="경국대전", keyword2="유교정치", keyword3="안정",
         summary="경국대전을 완성하며 유교 중심 국가 체계를 확립.",
         img_url="characters/seongjong.png"),
    dict(kor_name="연산군", hanja_name="燕山君", birth_to_death="1476-1506",
         keyword1="폭정",    keyword2="광기",    keyword3="감정적",
         summary="사사로운 감정으로 폭정을 일삼은 조선 최악의 군주.",
         img_url="characters/yeonsangun.jpg"),
    dict(kor_name="중종",   hanja_name="中宗",   birth_to_death="1488-1544",
         keyword1="반정",    keyword2="개혁시도", keyword3="불안정",
         summary="중종반정으로 왕위에 올랐지만 개혁과 정치 사이에서 흔들림.",
         img_url="characters/jungjong.png"),
    dict(kor_name="단종",   hanja_name="端宗",   birth_to_death="1441-1457",
         keyword1="비극",    keyword2="어린왕",  keyword3="충절",
         summary="세조에게 왕위를 빼앗기고 비극적인 운명을 맞이한 어린 왕.",
         img_url="characters/danjong.jpg"),
    dict(kor_name="광해군", hanja_name="光海君", birth_to_death="1575-1641",
         keyword1="외교",    keyword2="중립",    keyword3="실리주의",
         summary="명과 후금 사이에서 실리 외교를 펼친 현실적인 군주.",
         img_url="characters/gwanghae.png"),
    dict(kor_name="인조",   hanja_name="仁祖",   birth_to_death="1595-1649",
         keyword1="병자호란", keyword2="굴욕",   keyword3="보수적",
         summary="병자호란으로 굴욕적인 항복을 경험한 왕.",
         img_url="characters/injo.png"),
    dict(kor_name="정조",   hanja_name="正祖",   birth_to_death="1752-1800",
         keyword1="개혁",    keyword2="규장각",  keyword3="지식",
         summary="개혁 정치와 학문 진흥을 통해 조선 후기 중흥을 이끈 왕.",
         img_url="characters/jeongjo.png"),
]


class Command(BaseCommand):
    help = "독대 모드 캐릭터(왕) 초기 데이터를 DB에 삽입합니다."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="기존 데이터를 전부 삭제하고 새로 삽입합니다.")

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = CharModeInfo.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"기존 캐릭터 {deleted}개 삭제됨"))

        created_count = skipped_count = 0

        for data in CHARACTERS:
            obj, created = CharModeInfo.objects.get_or_create(
                kor_name=data["kor_name"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ 생성: {obj.kor_name} ({obj.hanja_name})")
            else:
                skipped_count += 1
                self.stdout.write(f"  ⏭️  스킵: {obj.kor_name}")

        self.stdout.write(self.style.SUCCESS(
            f"\n완료 — 생성: {created_count}개 / 스킵: {skipped_count}개"
        ))
