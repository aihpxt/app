"""用户贡献模块"""

import time
import random
from typing import Dict, Any, List, Optional

class UserContribution:
    """用户贡献类"""
    
    def __init__(self):
        """初始化用户贡献模块"""
        self.contributions = []  # 存储用户贡献的信息
        self.pending_contributions = []  # 待审核的贡献
        self.approved_contributions = []  # 已审核的贡献
        self.rejected_contributions = []  # 已拒绝的贡献
        self.contribution_id_counter = 1  # 贡献ID计数器
    
    def submit_contribution(self, contribution: Dict[str, Any]) -> Dict[str, Any]:
        """提交用户贡献
        
        Args:
            contribution: 用户贡献的信息，包含title, content, source, type, submitter等字段
            
        Returns:
            Dict[str, Any]: 提交结果，包含贡献ID和状态
        """
        # 生成贡献ID
        contribution_id = f"contribution_{self.contribution_id_counter}"
        self.contribution_id_counter += 1
        
        # 完善贡献信息
        contribution_data = {
            "id": contribution_id,
            "title": contribution.get("title", ""),
            "content": contribution.get("content", ""),
            "source": contribution.get("source", "用户贡献"),
            "type": contribution.get("type", "other"),
            "submitter": contribution.get("submitter", "匿名用户"),
            "submit_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": "pending",  # 初始状态为待审核
            "reviewer": None,
            "review_time": None,
            "review_notes": None
        }
        
        # 添加到贡献列表
        self.contributions.append(contribution_data)
        self.pending_contributions.append(contribution_data)
        
        return {
            "status": "success",
            "message": "贡献提交成功，等待审核",
            "contribution_id": contribution_id
        }
    
    def review_contribution(self, contribution_id: str, status: str, reviewer: str, notes: str = "") -> Dict[str, Any]:
        """审核用户贡献
        
        Args:
            contribution_id: 贡献ID
            status: 审核状态，approved或rejected
            reviewer: 审核人
            notes: 审核备注
            
        Returns:
            Dict[str, Any]: 审核结果
        """
        for contribution in self.contributions:
            if contribution["id"] == contribution_id:
                # 更新贡献状态
                contribution["status"] = status
                contribution["reviewer"] = reviewer
                contribution["review_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
                contribution["review_notes"] = notes
                
                # 从待审核列表中移除
                self.pending_contributions = [c for c in self.pending_contributions if c["id"] != contribution_id]
                
                # 添加到对应状态的列表
                if status == "approved":
                    self.approved_contributions.append(contribution)
                elif status == "rejected":
                    self.rejected_contributions.append(contribution)
                
                return {
                    "status": "success",
                    "message": f"贡献审核成功，状态更新为{status}"
                }
        
        return {
            "status": "error",
            "message": "贡献不存在"
        }
    
    def get_contributions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户贡献
        
        Args:
            status: 贡献状态，可选值为pending, approved, rejected
            
        Returns:
            List[Dict[str, Any]]: 贡献列表
        """
        if status:
            if status == "pending":
                return self.pending_contributions
            elif status == "approved":
                return self.approved_contributions
            elif status == "rejected":
                return self.rejected_contributions
            else:
                return []
        else:
            return self.contributions
    
    def get_contribution_by_id(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取贡献
        
        Args:
            contribution_id: 贡献ID
            
        Returns:
            Optional[Dict[str, Any]]: 贡献信息
        """
        for contribution in self.contributions:
            if contribution["id"] == contribution_id:
                return contribution
        return None
    
    def get_contribution_stats(self) -> Dict[str, Any]:
        """获取贡献统计信息
        
        Returns:
            Dict[str, Any]: 贡献统计信息
        """
        stats = {
            "total": len(self.contributions),
            "pending": len(self.pending_contributions),
            "approved": len(self.approved_contributions),
            "rejected": len(self.rejected_contributions),
            "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return stats
    
    def export_approved_contributions(self) -> List[Dict[str, Any]]:
        """导出已审核通过的贡献
        
        Returns:
            List[Dict[str, Any]]: 已审核通过的贡献列表
        """
        # 转换为标准数据格式
        exported_contributions = []
        for contribution in self.approved_contributions:
            exported_contribution = {
                "title": contribution["title"],
                "content": contribution["content"],
                "url": f"/contribution/{contribution['id']}",
                "date": contribution["submit_time"].split()[0],
                "source": contribution["source"],
                "type": contribution["type"],
                "crawled_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            exported_contributions.append(exported_contribution)
        
        return exported_contributions

# 全局用户贡献实例
user_contribution = UserContribution()