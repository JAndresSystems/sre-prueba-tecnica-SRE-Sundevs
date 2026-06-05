import json
import hashlib
import os
import boto3
import redis
from datetime import datetime
import uuid


s3_client = boto3.client("s3")


BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

def get_redis_client():
    
    return redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )

def generate_cache_key(body: dict) -> str:
    
    body_string = json.dumps(body, sort_keys=True)
    return hashlib.sha256(body_string.encode()).hexdigest()

def process_data(body: dict) -> dict:
    
    body_string = json.dumps(body, sort_keys=True)
    result_hash = hashlib.sha256(body_string.encode()).hexdigest()

    return {
        "resultado": result_hash,
        "datos_originales": body,
        "procesado_en": datetime.utcnow().isoformat()
    }

def save_to_s3(result: dict, result_id: str) -> str:
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    s3_key = f"results/{today}/{result_id}.json"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(result),
        ContentType="application/json"
    )

    return s3_key

def handler(event, context):
    
    try:
        
        print(f"Event recibido: {json.dumps(event)}")
        
        body_raw = event.get("body", "{}")
        print(f"Body raw: {body_raw}")
        
        body = json.loads(body_raw) if body_raw else {}
        print(f"Body parseado: {body}")

        
        cache_key = generate_cache_key(body)
        print(f"Cache key: {cache_key}")

        
        try:
            redis_client = get_redis_client()
            cached_value = redis_client.get(cache_key)
            print(f"Cache resultado: {cached_value}")
        except Exception as redis_error:
            print(f"ERROR Redis: {str(redis_error)}")
            cached_value = None

        if cached_value:
        
            print("CACHE HIT - devolviendo valor cacheado")
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "X-Cache": "HIT"
                },
                "body": cached_value
            }

        
        print("CACHE MISS - procesando request")
        result = process_data(body)
        result_id = str(uuid.uuid4())

        
        s3_key = save_to_s3(result, result_id)
        result["s3_key"] = s3_key
        print(f"Guardado en S3: {s3_key}")

        
        try:
            redis_client.setex(
                cache_key,
                60,
                json.dumps(result)
            )
            print(f"Guardado en Redis con TTL 60s")
        except Exception as redis_error:
            print(f"ERROR guardando en Redis: {str(redis_error)}")

        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Cache": "MISS"
            },
            "body": json.dumps(result)
        }

    except Exception as e:
        print(f"ERROR general: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "X-Cache": "ERROR"
            },
            "body": json.dumps({
                "error": "Error interno del servidor",
                "detalle": str(e)
            })
        }
