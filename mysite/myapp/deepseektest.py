# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="api키 복붙하세요", base_url="https://api.deepseek.com")



response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": """당신은 초보자를 위한 코드리뷰 선생님입니다. 
        사용되는 어휘는 쉽게 풀어서 설명해야 하며, 코드 리뷰 시에 너무 어려운 개념은 고려하지말고 기본을 잘 지켰는지, 문제되는 부분이 없는지를 중점으로 리뷰를해주세요. 
        리뷰는 너무 단호한 어조가 아닌 친절한 어조로 격려를 동반해야합니다.
        청중은 코딩을 시작한지 얼마 되지 않은 초보자이기에 어려운 용어나 개념을 잘 알지 못합니다.
        작성된 코드를 꼼꼼히 읽어보면서 리뷰를 해주세요, 불필요한 코드 조각이 있다면 짚어주며 코드를 지우길 권장해주고
        그리고 만약 문제점을 찾아냈다면 해당 문제점을 짚어주며 쉬운 어휘로 풀어서 리뷰를 남겨주시길 바랍니다
        그리고 해당 문제를 다시 겪지 않기 위해 공부해야할 학습 방향도 같이 추천해주세요
        """},        {"role": "user", "content": '''
        package lotto.service;

import java.math.BigDecimal;
import java.util.Map;
import lotto.domain.dto.LottoResult;
import java.util.List;

public class CalculateService {

    public BigDecimal calculateRatio(int amount, Map<LottoResult, Integer> drawResult) {
        BigDecimal ratio = BigDecimal.valueOf(calculatePrize(drawResult))
                .divide(BigDecimal.valueOf(amount))
                .multiply(BigDecimal.valueOf(100))
                .stripTrailingZeros(); // 뒤에 불필요한 0 제거
        return new BigDecimal(ratio.toPlainString()); // 일반 숫자 형식으로 변환
    }

    private int calculatePrize(Map<LottoResult, Integer> drawResult) {
        int sum = 0;
        for (LottoResult lottoResult : drawResult.keySet()) {
            int matchingNumberCount = lottoResult.getMatchingNumberCount();
            sum = getSum(lottoResult, drawResult.get(lottoResult), matchingNumberCount, sum);
        }
        return sum;
    }

    private int getSum(LottoResult lottoResult, int count, int matchingNumberCount, int sum) {
        if (matchingNumberCount==5) {
            return calculateFive(lottoResult, count, sum);
        }
        return calculateOthers(lottoResult, sum);
    }

    private static int calculateOthers(LottoResult lottoResult, int sum) {
        if (lottoResult.isBonusMatch()) {
            sum += MatchPrize.getPrizeByMatchCount(lottoResult.getMatchingNumberCount() + 1);
            return sum;
        }
        sum += MatchPrize.getPrizeByMatchCount(lottoResult.getMatchingNumberCount());
        return sum;
    }

    private static int calculateFive(LottoResult lottoResult, int count, int sum) {
        if (lottoResult.isBonusMatch()) {
            sum += (MatchPrize.FIVE_MATCH_WITH_BONUS.getPrize() * count);
            return sum;
        }
        sum += (MatchPrize.FIVE_MATCH.getPrize() * count);
        return sum;
    }


}

코드 리뷰를 남겨주세요

결과는 이 코드에 대한 총평과 점수(10점 만점)를 포함해주세요
만약 1~6점 사이의 점수를 받았다면, 해당 코드는 문제코드로 판단하여 문제 유형을 설정해주세요 (ex: 클린 코드 / 성능 및 최적화)
(이때 점수가 7~10점 사이라면 문제유형은 비워서 반환해주세요)

문제유형은 가장 문제인 한가지 항목이어야 합니다
        '''},
    ],
    stream=False
)

print(response.choices[0].message.content)