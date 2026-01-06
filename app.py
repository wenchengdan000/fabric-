# 存储结果的列表
results = []
# 获取当前日期
today = datetime.now().strftime("%Y-%m-%d")

print(f"正在处理域名: {domain}")
tenant_id, client_id, client_secret, pageid = get_tenant(databaseid_get_tenant, domain, notionapi)
print(f"tenant_id: {tenant_id}")

if tenant_id and client_id and client_secret:
    try:
        access_token = generate_token(tenant_id, client_id, client_secret)
        print("已获取 access token")
        
        # 获取许可证信息
        graph_url = 'https://graph.microsoft.com/v1.0/subscribedSkus'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        # Add timeout to prevent hanging on slow connections
        response = requests.get(graph_url, headers=headers, timeout=30)

        # 处理许可证信息
        if response.status_code == 200:
            licenses = response.json().get('value', [])
            for license in licenses:
                sku_id = license['skuId']
                sku_part_number = license['skuPartNumber']
                prepaid_units = license['prepaidUnits']
                # Use next() for more efficient search - stops at first match
                status = next((key for key, value in prepaid_units.items() if value > 0), None)
                # 如果没有大于 0 的值，使用 capabilityStatus
                if status is None:
                    status = license['capabilityStatus']
                results.append([today, domain, sku_id, sku_part_number, status])
        else:
            print(f"获取许可证失败: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"网络请求异常: {e}")
    except KeyError as e:
        print(f"API响应缺少必需字段: {e}")
    except ValueError as e:
        print(f"数据值错误: {e}")
    except Exception as e:
        print(f"发生异常: {e}")
else:
    print("获取 tenant 信息失败")

# 打印结果
if results:
    df_results = pd.DataFrame(results, columns=['日期', '域名', 'SKU ID', 'SKU Part Number', 'Status'])
    print(df_results)
else:
    print("无结果")


