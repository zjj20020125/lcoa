<template>
  <div class="project-settings">
    <h2>⚙️ 项目设置</h2>
    <div class="settings-content">
      <p>这是项目设置页面，用于配置项目相关参数。</p>
      <div class="settings-form">
        <div class="form-group">
          <label>项目名称</label>
          <input type="text" placeholder="请输入项目名称">
        </div>
        <div class="form-group">
          <label>项目描述</label>
          <textarea placeholder="请输入项目描述"></textarea>
        </div>
        <div class="form-group">
          <label>默认负责人</label>
          <select>
            <option>请选择负责人</option>
            <option>张三</option>
            <option>李四</option>
            <option>王五</option>
          </select>
        </div>
        <div class="form-group">
          <label>项目状态</label>
          <select>
            <option>进行中</option>
            <option>待开始</option>
            <option>已完成</option>
            <option>已暂停</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="save-btn">保存设置</button>
          <button class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectSettings'
}
</script>

<style scoped>
.project-settings {
  padding: 20px;
}

.project-settings h2 {
  color: #333;
  margin-bottom: 20px;
}

.settings-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:hover {
  background-color: #45a049;
}

.cancel-btn {
  background-color: #f5f7fa;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}
</style>