// 登录表单校验规则
export const loginRules = {
  username: [
    {
      required: true,
      message: '用户名不为空',
      trigger: 'blur', // 失去焦点时触发校验
    },
  ],
  password: [
    {
      required: true,
      message: '密码不为空',
      trigger: 'blur',
    },
    {
      min: 6,
      max: 12,
      required: true,
      message: '密码长度为6-12字符',
      trigger: 'blur',
    },
  ],
  agree: [
    {
      validator: (rule, value, callback) => {
        //自定义检验逻辑
        //勾选过 不勾选不过
        if (value) {
          callback()
        } else {
          callback(new Error('请勾选我们的协议'))
        }
      },
    },
  ],
  email: [
    {
      required: true,
      message: '邮箱不能为空',
      trigger: 'blur',
    },
    {
      // 新增：邮箱格式正则验证
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      message: '请输入有效的邮箱地址（如：example@domain.com）',
      trigger: 'blur',
    },
    {
      // 修正：原错误的密码长度提示，改为邮箱长度限制（可选）
      min: 6,
      max: 50, // 邮箱长度放宽到50字符（更符合实际）
      message: '邮箱长度为6-50字符',
      trigger: 'blur',
    },
  ],
}
