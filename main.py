import requests
import os
# --- 配置区 ---
API_TOKEN = os.getenv('CF_API_TOKEN')
ZONE_ID = os.getenv('CF_ZONE_ID')
DOMAIN_NAME = "youxuan.xiaodu1234.xyz"  # 你要解析到的完整域名

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

headers1 = {
    "Content-Type": "application/json"
}

def get_existing_records():
    """获取该域名下所有现有的 A 记录 ID"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    params = {"name": DOMAIN_NAME, "type": "A"}
    res = requests.get(url, headers=headers, params=params).json()
    return [record['id'] for record in res.get('result', [])]


def delete_record(record_id):
    """删除旧记录"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    requests.delete(url, headers=headers)


def add_record(ip):
    """添加新记录"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    data = {
        "type": "A",
        "name": DOMAIN_NAME,
        "content": ip,
        "ttl": 60,  # 优选IP建议TTL设短一点，方便快速切换
        "proxied": False  # 优选IP通常必须关闭小黄云（不经过CF CDN代理）
    }
    res = requests.post(url, headers=headers, json=data).json()
    if res.get('success'):
        print(f"✅ 成功解析 IP: {ip}")
    else:
        print(f"❌ 解析失败 {ip}: {res.get('errors')}")


def record():
    print(f"开始处理域名: {DOMAIN_NAME}")

    data = {
        "key": "iDetkOys"
    }
    res = requests.post('https://api.hostmonit.com/get_optimization_ip', headers=headers1, json=data).json()
    ips = []
    for ip in res.get('info'):
        ips.append(ip.get('ip'))

    print('优选ips', ips)

    if len(ips) == 0:
        return

    ips = ips[:2]
    ips.append('162.159.129.53')

    # 1. 清理旧记录（防止记录堆积）
    old_ids = get_existing_records()
    for rid in old_ids:
        delete_record(rid)
    print(f"已清理 {len(old_ids)} 条旧记录")

    # 2. 批量添加新记录
    for ip in ips:
        add_record(ip)

# --- 执行流程 ---
if __name__ == "__main__":
    record()