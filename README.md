## 使用说明

填写config中信息（必填jar_path）

用带有官方包的代码构建jar包

支持对单独文件的正确性检验

出现bug可以在github提出issue，我们尽快解决

*点点star谢谢（*

## config说明：

### 测试相关
test_num：为测试样例数

basic_command_num：为指令数

jar_path：为jar包的路径

del_temp_file：删除正确样例

### 数据生成相关
基础指令:query, borrow, order

生成指令:pick, return

begin_date: 最早起始日期  

end_date: 最晚结束日期

max_num_of_days_with_command: 拥有基础指令的天数最大值

max_num_of_book_identifier: 每个类别书的标识符数目最大值

max_num_of_book_for_each_identifier: 每种书的数目最大值

max_num_of_person: 人数最大值

borrow_prob：生成借书指令概率

query_prob：生成查询概率概率

order_prob：生成预约概率

return_prob：对于每个成功的borrow，生成归还指令的概率

pick_1_prob：对于每个成功的order，生成1个pick指令的概率

pick_2_prob：对于每个成功的order，生成2个pick指令的概率

### 单文件检验
input_file: 输入文件路径

output_file: 输出文件路径

将完整输入与完整输出放置到两个文件中，并填写config中以上2个 ，运行Checker.py即可

## 数据生成逻辑
1. 在一定天数范围内随机生成基础指令
2. 对成功的某些特定基础指令，生成生成指令，其中return指令将在当前天数和截止天数间随机生成； pick指令将在当前天数和(当前天数+12)间随机生成

## 注意
为保证数据的强度，不建议将时间范围、max_num_of_book_identifier、max_num_of_book_for_each_identifier、max_num_of_person设置过大

max_num_of_days_with_command需大于begin_date和end_date的差值

对于return指令可能有bug，我以添加调试信息，不影响评测

## 关于Bug

目前数据生成极小有bug，可能会在一条borrow指令后生成两条return指令从而出错。bug原因正在排查（排查不出啊！！！！！！！！）

如果知道bug原因可以与我联系