from django.apps import AppConfig


class VotingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voting'

    def ready(self):
        """Load blockchain from DB when server starts."""
        try:
            from .blockchain import get_blockchain, Block
            from .models import VoteBlock
            bc = get_blockchain()
            vbs = VoteBlock.objects.all().order_by('index')
            if vbs.exists():
                bc.chain = bc.chain[:1]  # keep genesis
                for vb in vbs:
                    block = Block(
                        index=vb.index,
                        user_id_hash=vb.user_id_hash,
                        candidate=vb.candidate,
                        timestamp=vb.timestamp,
                        previous_hash=vb.previous_hash,
                    )
                    block.hash = vb.block_hash
                    bc.chain.append(block)
        except Exception:
            pass  # DB may not be ready during initial migration
