import os
import math
import random
import string
import pickle
import shutil
from pathlib import Path
from collections import Counter
import numpy as np
import os
import random
import pickle
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
from dotenv import load_dotenv


def log_normal(mu=9.96915, sigma=1.63005) -> int:
    """Sample an integer from a lognormal distribution with parameters mu and sigma."""
    x = np.random.lognormal(mean=mu, sigma=sigma)
    return int(x)

def rand_words(n_words: int) -> str:
    words = []
    for _ in range(n_words):
        wlen = random.randint(2, 10)
        w = "".join(random.choice(string.ascii_lowercase) for _ in range(wlen))
        words.append(w)
    return " ".join(words)

def unique_name(idx: int, path) -> Path:
    return Path(path) / f"{idx:04d}.txt"

def write_txt(path: Path, text: str):
    data = text.encode("ascii", errors="ignore")
    if not data:
        data = b"\n"
    with open(path, "wb") as f:
        f.write(data)

def _worker_init(model_path: str, seed: int | None):
    global DICT3, DICT2, DICT1, DICT3_KEYS
    with open(model_path, "rb") as f:
        DICT3, DICT2, DICT1 = pickle.load(f)
    DICT3_KEYS = list(DICT3.keys())
    if seed is not None:
        random.seed(seed + os.getpid())

def _sample_from_counter(counter: Counter) -> str:
    items = list(counter.items())
    tokens, weights = zip(*items)
    return random.choices(tokens, weights=weights, k=1)[0]

def sized_markov(target_bytes: int) -> str:
    if target_bytes <= 0:
        return ""

    state3 = random.choice(DICT3_KEYS)
    tokens = list(state3)
    size = sum(len(t.encode("utf-8")) for t in tokens) + (len(tokens) - 1)

    while size < target_bytes:
        t3 = (tokens[-3], tokens[-2], tokens[-1])
        t2 = (tokens[-2], tokens[-1])
        t1 = tokens[-1]

        if t3 in DICT3:
            nxt = _sample_from_counter(DICT3[t3])
        elif t2 in DICT2:
            nxt = _sample_from_counter(DICT2[t2])
        elif t1 in DICT1:
            nxt = _sample_from_counter(DICT1[t1])
        else:
            state3 = random.choice(DICT3_KEYS)
            for tok in state3:
                size += 1 + len(tok.encode("utf-8"))
                tokens.append(tok)
            continue

        size += 1 + len(nxt.encode("utf-8"))
        tokens.append(nxt)

    b = (" ".join(tokens)).encode("utf-8")[:target_bytes]
    return b.decode("utf-8", errors="ignore")


def _make_one_file(job):
    path_str, target_bytes = job
    path = Path(path_str)
    text = sized_markov(target_bytes)
    write_txt(path, text)
    return path.stat().st_size

def generate_markov(
    model_path: str,
    root_path: str | Path,
    num_files: int,
    workers: int = 6,
    seed: int | None = 1234,
):

    root = Path(root_path)
    root.mkdir(parents=True, exist_ok=True)
    
    jobs = []
    for file_count in range(1, num_files + 1):
        target = log_normal()
        path = root / f"file_{file_count:06d}.txt"
        jobs.append((str(path), target))
    
    total_written = 0
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_worker_init,
        initargs=(model_path, seed),
    ) as ex:
        futures = [ex.submit(_make_one_file, job) for job in jobs]
        for fut in as_completed(futures):
            actual = fut.result()
            total_written += actual
            # print(f"+{actual:,} bytes, total={total_written/(1024**3):.2f} GiB")
    
    # print(f"Done. Wrote {total_written/(1024**3):.2f} GiB across {num_files} files into {root.resolve()}")

def copy_random_files_with_randomized_types(
    source_dir: Path,
    dest_dir: Path,
    num_files: int,
    seed: int | None = None,
    preserve_tree: bool = False,
    min_size_bytes: int = 1024,  # floor
):
    if seed is not None:
        random.seed(seed)
    
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    total_written = 0
    file_count = 0
    
    all_files = [
        p for p in source_dir.rglob("*") 
        if p.is_file() and not p.is_symlink() and p.stat().st_size >= min_size_bytes
    ]
    random.shuffle(all_files)
    
    for src in all_files:
        if file_count >= num_files:
            break
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        if preserve_tree:
            rel = src.relative_to(source_dir)
            out_path = dest_dir / rel
            out_path = out_path.with_suffix("." + 'txt')
            out_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            out_path = dest_dir / f"file_{file_count+1:06d}.txt"
        
        if out_path.exists():
            stem = out_path.stem
            suffix = out_path.suffix
            i = 1
            while out_path.exists():
                out_path = out_path.with_name(f"{stem}_{i}{suffix}")
                i += 1
    
        try:
            write_txt(out_path, text)
            actual = out_path.stat().st_size
            total_written += actual
            file_count += 1
            # print(f"{out_path.name}: +{actual:,} bytes, total written={total_written/(1024**3):.2f} GiB, files={file_count}/{num_files}")
        except:
            continue
    
    # print(f"\nDone. Wrote {file_count} files ({total_written/(1024**3):.2f} GiB) into {dest_dir.resolve()}")



def generate_files_to_count_main(generator_func:str, root_path, num_files):
    def loop_generators(generator_func, root_path, num_files):
        min_file_bytes = 4 * 1024 ; max_file_bytes = 200 * 1024**2
        total_written = 0
        for file_count in range(1, num_files + 1):
            target = log_normal()
            target = max(min_file_bytes, min(target, max_file_bytes))
            
            text = generator_func(target)
            path = unique_name(file_count, root_path)
            write_txt(path, text)
            
            actual = path.stat().st_size
            total_written += actual
            # print(f"{path.name}: target={target:,} bytes, actual={actual:,} bytes, total={total_written/(1024**3):.3f} GiB")
        
        # print(f"\nDone. Wrote {total_written / (1024**3):.2f} GiB across {num_files} files into {root_path}")

    load_dotenv()
    shutil.rmtree(root_path, ignore_errors=True)
    root_path.mkdir(parents=True, exist_ok=True)

    if generator_func == 'zeros':
        loop_generators(sized_zeros, root_path, num_files)
    elif generator_func == 'random':
        loop_generators(sized_dev_random, root_path, num_files)
    elif generator_func == 'markov':
        generate_markov(
            model_path="data/markov/markov_model.pkl",
            root_path=root_path,
            num_files=num_files,
            # workers=os.cpu_count()//2
            workers=2
            )
    elif generator_func == 'enron':
        copy_random_files_with_randomized_types(
            source_dir=Path(os.getenv('ENRON_PATH')),
            dest_dir=root_path,
            num_files=num_files,
            seed=1234
            )
    elif generator_func == 'contracts':
        copy_random_files_with_randomized_types(
            source_dir=Path(os.getenv('CONTRACTS_PATH')),
            dest_dir=root_path,
            num_files=num_files,
            seed=1234
            )



def sized_dev_random(target_bytes: int, *, source: str = "urandom") -> str:
    raw_needed = math.ceil(target_bytes / 2)
    raw = os.urandom(raw_needed) if source == "urandom" else open("/dev/random", "rb", buffering=0).read(raw_needed)
    txt = raw.hex()
    return txt[:target_bytes]

def sized_zeros(target_bytes: int):
        return '0' * target_bytes

DICT3 = DICT2 = DICT1 = None
DICT3_KEYS = None
if __name__ == '__main__':
    root_path = Path('data/outputs/test/')
    generate_files_to_count_main('contracts', root_path, 5)