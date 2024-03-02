from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class IntroCourse(models.Model):
    TEXT_TYPES = (
        ('heading', '見出し'),
        ('text', 'テキスト'),
        ('red', '赤枠'),
        ('yellow', '黄枠'),
        ('blue', '青枠'),
        ('green', '緑枠'),
        ('img', '画像'))
    
    title = models.CharField(max_length=60,verbose_name="タイトル")
    section = models.PositiveIntegerField(verbose_name="区分")
    order = models.PositiveSmallIntegerField(verbose_name="順番")
    text_type = models.CharField(max_length=20, choices=TEXT_TYPES, verbose_name="タイプ", blank=True)
    content = models.TextField(blank=True, verbose_name="内容")

    def add_title(self):
        if self.text_type == 'heading':
            return str(self.order) + self.content
        elif self.text_type == 'red':
            return str(self.order) + "🟥"
        elif self.text_type == 'yellow':
            return str(self.order) + "🟨"
        elif self.text_type == 'blue':
            return str(self.order) + "🟦"
        elif self.text_type == 'green':
            return str(self.order) + "🟩"
        else:
            return str(self.order)
        
    def __str__(self):
        return self.title + self.add_title()


class Basis(models.Model):
    title = models.CharField(max_length=60,verbose_name="問題内容")
    unit = models.PositiveIntegerField(verbose_name="大区分")
    section = models.PositiveSmallIntegerField(verbose_name="小区分")
    category = models.SmallIntegerField(verbose_name="分類")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文")
    pre_code = models.TextField(blank=True, verbose_name="指定入力（前）")
    pre_visual = models.TextField(blank=True, verbose_name="入力視像（前）")
    post_code = models.TextField(blank=True, verbose_name="指定入力（後）")
    post_visual = models.TextField(blank=True, verbose_name="入力視像（後）")
    i_range = models.TextField(blank=True, verbose_name="範囲[]/gvc/")
    g_range = models.TextField(blank=True, verbose_name="範囲の範囲")
    role_code = models.TextField(blank=True, verbose_name="演算コード")
    q_data = models.TextField(blank=True, verbose_name="出題データ/Qend")
    c_output = models.TextField(blank=True, verbose_name="要求出力/Qend")
    e_answer = models.TextField(blank=True, verbose_name="解答例/Qend")
    explanation = models.TextField(blank=True, verbose_name="解説")
    q_key = models.BooleanField(verbose_name="フィルター用", default=False)
    major_h = models.CharField(blank=True, max_length=20, verbose_name="問題グループ")#q_keyがTrueの時のみ
    minor_h = models.CharField(blank=True, max_length=20, verbose_name="問題名")#q_keyがTrueの時のみ


    def __str__(self):
        return self.title

class Quartet(models.Model):
    primary_key = models.PositiveIntegerField(primary_key=True, verbose_name="primary_key")
    title = models.CharField(blank=True, max_length=60,verbose_name="問題名")
    unit = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="大区分")
    section = models.PositiveIntegerField(verbose_name="区分")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文", default="以下のコードを実行した時の出力として正しいものを選択してください。")
    question_code = models.TextField(blank=True,verbose_name="問題（コード）")
    choices1 = models.TextField(blank=True, verbose_name="選択肢1")
    choices2 = models.TextField(blank=True, verbose_name="選択肢2")
    choices3 = models.TextField(blank=True, verbose_name="選択肢3")
    choices4 = models.TextField(blank=True, verbose_name="選択肢4")
    answer_idx = models.PositiveSmallIntegerField(verbose_name="解答番号")
    frame = models.BooleanField(default = False, verbose_name="枠")
    explanation = models.TextField(blank=True, verbose_name="解説")

    def __str__(self):
        return str(self.primary_key) + '.' + self.title
    
class QuartetResult(models.Model):
    user_id = models.PositiveIntegerField(verbose_name="ユーザーID")
    result = models.BooleanField(blank=True, null=True, verbose_name="結果")
    connection_key = models.ForeignKey(Quartet, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return str(self.user_id) + '-' + str(self.connection_key)


class Competition(models.Model):
    primary_key = models.PositiveIntegerField(primary_key=True, verbose_name="primary_key")
    title = models.CharField(max_length=60,verbose_name="問題名")
    section = models.PositiveIntegerField(verbose_name="区分")
    level = models.PositiveSmallIntegerField(verbose_name="難易度")
    question = models.TextField(verbose_name="問題文")
    input_format = models.TextField(verbose_name="入力フォーマット", blank=True)
    expectation = models.TextField(verbose_name="期待出力", blank=True)
    condition = models.TextField(verbose_name="条件", blank=True)
    input_ex = models.TextField(verbose_name="入力例", default = "/separate/")
    output_ex = models.TextField(verbose_name="出力例", default = "/separate/")
    input_data = models.TextField(verbose_name="入力データ", default = "/separate/")
    output_data = models.TextField(verbose_name="出力データ", default = "/separate/")
    e_answer = models.TextField(blank=True, verbose_name="解答例")
    explanation = models.TextField(blank=True, verbose_name="解説")

    def __str__(self):
        return self.title

class CompeResult(models.Model):
    user_id = models.PositiveIntegerField(verbose_name="ユーザーID")
    result = models.BooleanField(blank=True, null=True, verbose_name="結果")
    connection_key = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return str(self.user_id) + '-' + str(self.connection_key)