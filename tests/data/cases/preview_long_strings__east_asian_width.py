# flags: --unstable
# The following strings do not have not-so-many chars, but are long enough
# when these are rendered in a monospace font (if the renderer respects
# Unicode East Asian Width properties).
hangul = '코드포인트 수는 적으나 실제 터미널이나 에디터에서 렌더링될 땐 너무 길어서 줄바꿈이 필요한 문자열'
hanzi = '中文測試：代碼點數量少，但在真正的終端模擬器或編輯器中呈現時太長，因此需要換行的字符串。'
japanese = 'コードポイントの数は少ないが、実際の端末エミュレータやエディタでレンダリングされる時は長すぎる為、改行が要る文字列'
khmer = 'សម្រស់ទាវ២០២២ មិនធម្មតា ឥឡូវកំពុងរកតួ នេនទុំ និងពេជ្រ ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ'
# Should stay the same
khmer_same = [
    "text, expected_language",
    [
        (
            (
                "សម្រស់ទាវ២០២២ មិនធម្មតា ឥឡូវកំពុងរកតួ នេនទុំ និងពេជ្រ"
                " ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ "
            ),
            "km",
        ),  # Khmer
    ],
]

# output

# The following strings do not have not-so-many chars, but are long enough
# when these are rendered in a monospace font (if the renderer respects
# Unicode East Asian Width properties).
hangul = (
    "코드포인트 수는 적으나 실제 터미널이나 에디터에서 렌더링될 땐 너무 길어서 줄바꿈이"
    " 필요한 문자열"
)
hanzi = (
    "中文測試：代碼點數量少，但在真正的終端模擬器或編輯器中呈現時太長，"
    "因此需要換行的字符串。"
)
japanese = (
    "コードポイントの数は少ないが、"
    "実際の端末エミュレータやエディタでレンダリングされる時は長すぎる為、"
    "改行が要る文字列"
)
khmer = (
    "សម្រស់ទាវ២០២២ មិនធម្មតា ឥឡូវកំពុងរកតួ នេនទុំ និងពេជ្រ"
    " ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ"
)
# Should stay the same
khmer_same = [
    "text, expected_language",
    [
        (
            (
                "សម្រស់ទាវ២០២២ មិនធម្មតា ឥឡូវកំពុងរកតួ នេនទុំ និងពេជ្រ"
                " ប្រញាប់ឡើងទាន់គេមានបញ្ហាត្រូវថតឡើងវិញ "
            ),
            "km",
        ),  # Khmer
    ],
]