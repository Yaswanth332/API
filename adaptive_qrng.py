# adaptive_qrng.py
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def adaptive_rotation_qrng(
    n_qubits=4,
    shots=2048,
    iterations=8,
    warmup=2,
    init_theta=math.pi/2,
    lr=0.5,
    backend=None,
    seed_simulator=None,
    seq_length=10,
    num_seqs=20,
    tolerance=0.009  # max allowed difference between P(0) and P(1)
):
    """
    Adaptive-rotation QRNG using the Sdg -> Rx(theta) -> S gate sequence per qubit.

    Returns:
      - history: list of dicts {iter, thetas, p1}
      - sequences: list of random bit sequences (strings of length seq_length)
      - probs: dict with overall percentages {'P(0)%': ..., 'P(1)%': ...}
    """
    if backend is None:
        backend = AerSimulator()

    target_bits = seq_length * num_seqs

    while True:  # loop until balance condition is satisfied
        thetas = [init_theta] * n_qubits
        history = []
        collected_bits = []

        for it in range(iterations + warmup):
            if len(collected_bits) >= target_bits:
                break

            qc = QuantumCircuit(n_qubits, n_qubits)
            for q in range(n_qubits):
                qc.sdg(q)
                qc.rx(thetas[q], q)
                qc.s(q)
            qc.barrier()
            qc.measure(range(n_qubits), range(n_qubits))

            tqc = transpile(qc, backend)
            job = backend.run(tqc, shots=shots, seed_simulator=seed_simulator, memory=True)
            result = job.result()

            mem = result.get_memory()
            mem_rev = [s[::-1] for s in mem]

            # per-qubit probability of 1
            p1_list = []
            for q in range(n_qubits):
                ones = sum(int(s[q]) for s in mem_rev)
                p1 = ones / shots
                p1_list.append(p1)

            # update thetas
            for q in range(n_qubits):
                error = 0.5 - p1_list[q]
                thetas[q] += lr * error
                thetas[q] = max(0.0, min(math.pi, thetas[q]))

            if it >= warmup:
                for s in mem_rev:
                    collected_bits.extend(s)
                    if len(collected_bits) >= target_bits:
                        break

            history.append({
                'iter': it,
                'thetas': thetas.copy(),
                'p1': p1_list
            })

            print(f"iter {it}: mean p1 = {sum(p1_list)/len(p1_list):.4f}, "
                  f"thetas[0] = {thetas[0]:.4f}"
                  + (" (warmup)" if it < warmup else ""))

        # truncate
        collected_bits = collected_bits[:target_bits]

        # compute probabilities
        total_bits = len(collected_bits)
        ones = sum(int(b) for b in collected_bits)
        zeros = total_bits - ones
        p0 = zeros / total_bits
        p1 = ones / total_bits
        diff = abs(p0 - p1)

        # check balance
        if diff <= tolerance:
            break
        else:
            print(f"⚠️ Balance not satisfied (|P0-P1|={diff:.4f}), regenerating...")

    # split into sequences
    sequences = [
        ''.join(collected_bits[i:i+seq_length])
        for i in range(0, target_bits, seq_length)
    ]

    probs = {"P(0)%": p0 * 100, "P(1)%": p1 * 100}

    return history, sequences, probs


if __name__ == "__main__":
    hist, seqs, probs = adaptive_rotation_qrng(
        n_qubits=5,
        shots=2048,
        iterations=10,
        warmup=2,
        init_theta=math.pi/2,
        lr=0.5,
        seq_length=10,
        num_seqs=20,
        tolerance=0.009  # 0.9% max difference
    )
    print("\nGenerated random sequences (10 bits each, 20 total):")
    for i, s in enumerate(seqs, 1):
        print(f"Seq {i:02d}: {s}")
    print("\nOverall probabilities (%):", probs)